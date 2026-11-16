import { StyleSheet, Text } from "react-native";
import { useTranslation } from "react-i18next";

/** Shows the translated message for an API error code; nothing when there is no error. */
export function ErrorText({ code }: { code?: string }) {
  const { t } = useTranslation();
  if (!code) return null;
  return (
    <Text accessibilityRole="alert" accessibilityLiveRegion="polite" style={styles.error}>
      {t(`errors.${code}`, { defaultValue: t("errors.unknown") })}
    </Text>
  );
}

const styles = StyleSheet.create({ error: { color: "#b00020", fontSize: 14 } });
