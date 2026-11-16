import { Pressable, StyleSheet, Text } from "react-native";

type Props = { label: string; onPress: () => void; disabled?: boolean; variant?: "primary" | "secondary" };

export function Button({ label, onPress, disabled = false, variant = "primary" }: Props) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityState={{ disabled }}
      disabled={disabled}
      onPress={onPress}
      style={[styles.button, variant === "secondary" && styles.secondary, disabled && styles.disabled]}
    >
      <Text style={[styles.text, variant === "secondary" && styles.secondaryText]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: { backgroundColor: "#b5400f", borderRadius: 8, padding: 14, alignItems: "center", width: "100%" },
  secondary: { backgroundColor: "transparent", borderWidth: 1, borderColor: "#b5400f" },
  disabled: { opacity: 0.5 },
  text: { color: "#ffffff", fontSize: 16, fontWeight: "600" },
  secondaryText: { color: "#b5400f" },
});
