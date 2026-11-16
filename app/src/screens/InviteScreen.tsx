import { useLocalSearchParams, useRouter } from "expo-router";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Text, View } from "react-native";
import QRCode from "react-native-qrcode-svg";

import { api } from "../api/client";
import { errorCode } from "../api/errors";
import i18n, { type Language } from "../i18n";
import { Button } from "../ui/Button";
import { ErrorText } from "../ui/ErrorText";
import { Screen } from "../ui/Screen";
import { TextField } from "../ui/TextField";

type Enrolment = { uri: string; secret: string; token: string };

function secretFrom(uri: string): string {
  const match = /[?&]secret=([^&]+)/.exec(uri);
  return match ? decodeURIComponent(match[1]) : "";
}

export function InviteScreen() {
  const { t } = useTranslation();
  const router = useRouter();
  const { token } = useLocalSearchParams<{ token: string }>();
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [locale, setLocale] = useState<Language>(i18n.language === "en" ? "en" : "es");
  const [code, setCode] = useState("");
  const [enrolment, setEnrolment] = useState<Enrolment | null>(null);
  const [error, setError] = useState<string>();

  const accept = async () => {
    setError(undefined);
    try {
      const { data, error: apiError } = await api.POST("/api/invitations/accept", {
        body: { token: token ?? "", display_name: name, password, locale },
      });
      if (!data) return setError(errorCode(apiError));
      setEnrolment({ uri: data.provisioning_uri, secret: secretFrom(data.provisioning_uri), token: data.enrolment_token });
    } catch {
      setError("network");
    }
  };

  const confirm = async () => {
    if (!enrolment) return;
    setError(undefined);
    try {
      const { response, error: apiError } = await api.POST("/api/auth/totp/confirm", {
        body: { enrolment_token: enrolment.token, code },
      });
      if (!response.ok) return setError(errorCode(apiError));
      router.replace("/sign-in");
    } catch {
      setError("network");
    }
  };

  if (enrolment) {
    return (
      <Screen title={t("auth.invite.scanTitle")}>
        <Text>{t("auth.invite.scanHelp")}</Text>
        <View testID="totp-qr" accessible accessibilityLabel={t("auth.invite.qrLabel")}>
          <QRCode value={enrolment.uri} size={200} />
        </View>
        <Text>{t("auth.invite.manualSecret")}</Text>
        <Text selectable style={{ fontFamily: "monospace", fontSize: 16 }}>
          {enrolment.secret}
        </Text>
        <TextField
          label={t("auth.fields.code")}
          value={code}
          onChangeText={setCode}
          keyboardType="number-pad"
          autoComplete="one-time-code"
          maxLength={6}
        />
        <ErrorText code={error} />
        <Button label={t("auth.invite.confirm")} onPress={confirm} disabled={code.length !== 6} />
      </Screen>
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
