import { StyleSheet, Text, TextInput, View, type TextInputProps } from "react-native";

type Props = Omit<TextInputProps, "accessibilityLabel"> & { label: string };

/** Labelled text input. The visible label is also the accessible name. */
export function TextField({ label, style, ...input }: Props) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <TextInput accessibilityLabel={label} style={[styles.input, style]} {...input} />
    </View>
  );
}

const styles = StyleSheet.create({
  field: { gap: 4, width: "100%" },
  label: { fontSize: 14, fontWeight: "600" },
  input: { borderWidth: 1, borderColor: "#8a8a8a", borderRadius: 8, padding: 12, fontSize: 16 },
});
