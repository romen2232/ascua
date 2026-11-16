import { useLocalSearchParams, useRouter } from "expo-router";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Text, View } from "react-native";

import { api } from "../api/client";
import { errorCode } from "../api/errors";
import type { Enrolment } from "../auth/types";
import i18n, { type Language } from "../i18n";
import { Button } from "../ui/Button";
import { ErrorText } from "../ui/ErrorText";
import { Screen } from "../ui/Screen";
import { TextField } from "../ui/TextField";
import { TotpEnrolmentStep } from "./TotpEnrolmentStep";

export function InviteScreen() {
  const { t } = useTranslation();
  const router = useRouter();
  const { token } = useLocalSearchParams<{ token: string }>();
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [locale, setLocale] = useState<Language>(i18n.language === "en" ? "en" : "es");
  const [enrolment, setEnrolment] = useState<Enrolment | null>(null);
  const [error, setError] = useState<string>();

  const accept = async () => {
    setError(undefined);
    try {
      const { data, error: apiError } = await api.POST("/api/invitations/accept", {
        body: { token: token ?? "", display_name: name, password, locale },
      });
      if (!data) return setError(errorCode(apiError));
      setEnrolment({ uri: data.provisioning_uri, token: data.enrolment_token });
    } catch {
      setError("network");
    }
  };

  if (enrolment) {
    return (
      <TotpEnrolmentStep
        uri={enrolment.uri}
        enrolmentToken={enrolment.token}
        onConfirmed={() => router.replace("/sign-in")}
      />
    );
  }

  return (
    <Screen title={t("auth.invite.title")}>
      <TextField label={t("auth.fields.name")} value={name} onChangeText={setName} autoComplete="name" />
      <TextField
        label={t("auth.fields.password")}
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        autoComplete="new-password"
      />
      <Text>{t("auth.invite.language")}</Text>
      <View style={{ flexDirection: "row", gap: 8 }}>
        {(["es", "en"] as const).map((lang) => (
          <View key={lang} style={{ flex: 1 }}>
            <Button
              label={t(`languages.${lang}`)}
              variant={locale === lang ? "primary" : "secondary"}
              onPress={() => setLocale(lang)}
            />
          </View>
        ))}
      </View>
      <ErrorText code={error} />
      <Button label={t("auth.invite.submit")} onPress={accept} />
    </Screen>
  );
}
