import type { ReactNode } from "react";
import { ScrollView, StyleSheet, Text } from "react-native";

export function Screen({ title, children }: { title: string; children: ReactNode }) {
  return (
    <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
      <Text accessibilityRole="header" style={styles.title}>
        {title}
      </Text>
      {children}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, justifyContent: "center", padding: 24, gap: 16, maxWidth: 480, width: "100%", alignSelf: "center" },
  title: { fontSize: 28, fontWeight: "700" },
});
