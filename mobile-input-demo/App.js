// App.js — ChildSafeLens demo input screen.
//
// Flow: type a message -> Send -> call /predict -> if risky, show a nudge
// asking the sender to reconsider -> either way, log the event.

import React, { useState } from "react";
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Modal,
  StyleSheet,
  ScrollView,
} from "react-native";
import { predict, logEvent } from "./api";

export default function App() {
  const [message, setMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [nudgeVisible, setNudgeVisible] = useState(false);
  const [pendingLabel, setPendingLabel] = useState(null);
  const [pendingScore, setPendingScore] = useState(null);
  const [history, setHistory] = useState([]); // demo-only visible log

  async function handleSend() {
    if (!message.trim() || isSending) return;
    setIsSending(true);

    try {
      const { risk_score, is_risky, label } = await predict(message);

      if (is_risky) {
        // Hold the message, show the nudge, wait for the sender's choice.
        setPendingLabel(label);
        setPendingScore(risk_score);
        setNudgeVisible(true);
      } else {
        await finalizeSend(label, risk_score);
      }
    } catch (err) {
      addToHistory(`Error contacting server: ${err.message}`);
    } finally {
      setIsSending(false);
    }
  }

  async function finalizeSend(label, score) {
    await logEvent(label);
    addToHistory(`Sent — risk: ${label} (${score.toFixed(2)})`);
    setMessage("");
  }

  function addToHistory(line) {
    setHistory((prev) => [line, ...prev].slice(0, 8));
  }

  async function handleSendAnyway() {
    setNudgeVisible(false);
    await finalizeSend(pendingLabel, pendingScore);
  }

  function handleEditInstead() {
    setNudgeVisible(false);
    addToHistory(`Held for edit — risk: ${pendingLabel} (${pendingScore.toFixed(2)})`);
    // Message text stays in the input box so the sender can revise it.
  }

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>ChildSafeLens</Text>
      <Text style={styles.subtitle}>Demo — type a message and hit Send</Text>

      <TextInput
        style={styles.input}
        placeholder="Type a message..."
        value={message}
        onChangeText={setMessage}
        multiline
      />

      <TouchableOpacity
        style={[styles.button, isSending && styles.buttonDisabled]}
        onPress={handleSend}
        disabled={isSending}
      >
        <Text style={styles.buttonText}>{isSending ? "Checking..." : "Send"}</Text>
      </TouchableOpacity>

      <Text style={styles.historyTitle}>Recent activity</Text>
      <ScrollView style={styles.history}>
        {history.map((line, i) => (
          <Text key={i} style={styles.historyLine}>
            {line}
          </Text>
        ))}
      </ScrollView>

      <Modal visible={nudgeVisible} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            <Text style={styles.modalTitle}>Wait a second</Text>
            <Text style={styles.modalBody}>
              This message might come across as harmful. Want to reconsider
              before sending it?
            </Text>

            <TouchableOpacity style={styles.modalButtonPrimary} onPress={handleEditInstead}>
              <Text style={styles.modalButtonPrimaryText}>Edit message</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.modalButtonSecondary} onPress={handleSendAnyway}>
              <Text style={styles.modalButtonSecondaryText}>Send anyway</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F7F8FA", padding: 20 },
  title: { fontSize: 26, fontWeight: "700", color: "#1A1A2E", marginTop: 12 },
  subtitle: { fontSize: 14, color: "#6B7280", marginBottom: 20 },
  input: {
    minHeight: 90,
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#E5E7EB",
    padding: 14,
    fontSize: 16,
    textAlignVertical: "top",
  },
  button: {
    backgroundColor: "#4F46E5",
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 14,
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: "#FFFFFF", fontSize: 16, fontWeight: "600" },
  historyTitle: { marginTop: 28, fontSize: 14, fontWeight: "600", color: "#374151" },
  history: { marginTop: 8 },
  historyLine: { fontSize: 13, color: "#4B5563", paddingVertical: 4 },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.45)",
    justifyContent: "center",
    alignItems: "center",
    padding: 24,
  },
  modalCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 22,
    width: "100%",
  },
  modalTitle: { fontSize: 18, fontWeight: "700", color: "#1A1A2E", marginBottom: 8 },
  modalBody: { fontSize: 14, color: "#4B5563", marginBottom: 18, lineHeight: 20 },
  modalButtonPrimary: {
    backgroundColor: "#4F46E5",
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: "center",
    marginBottom: 10,
  },
  modalButtonPrimaryText: { color: "#FFFFFF", fontWeight: "600", fontSize: 15 },
  modalButtonSecondary: {
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#D1D5DB",
  },
  modalButtonSecondaryText: { color: "#374151", fontWeight: "600", fontSize: 15 },
});
