import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Text, View } from "react-native";
import QRCode from "react-native-qrcode-svg";

import { api } from "../api/client";
import { errorCode } from "../api/errors";
import { Button } from "../ui/Button";
import { ErrorText } from "../ui/ErrorText";
import { Screen } from "../ui/Screen";
import { TextField } from "../ui/TextField";

function secretFrom(uri: string): string {
  const match = /[?&]secret=([^&]+)/.exec(uri);
  return match ? decodeURIComponent(match[1]) : "";
}

type Props = { uri: string; enrolmentToken: string; onConfirmed: () => void };

/** QR code, manual key and 6-digit confirmation for setting up TOTP. */
export function TotpEnrolmentStep({ uri, enrolmentToken, onConfirmed }: Props) {
  const { t } = useTranslation();
  const [code, setCode] = useState("");
  const [error, setError] = useState<string>();

  const confirm = async () => {
    setError(undefined);
    try {
      const { response, error: apiError } = await api.POST("/api/auth/totp/confirm", {
        body: { enrolment_token: enrolmentToken, code },
      });
      if (!response.ok) return setError(errorCode(apiError));
      onConfirmed();
    } catch {
      setError("network");
    }
  };

  return (
    <Screen title={t("auth.invite.scanTitle")}>
      <Text>{t("auth.invite.scanHelp")}</Text>
      <View testID="totp-qr" accessible accessibilityLabel={t("auth.invite.qrLabel")}>
        <QRCode value={uri} size={200} />
      </View>
      <Text>{t("auth.invite.manualSecret")}</Text>
      <Text selectable style={{ fontFamily: "monospace", fontSize: 16 }}>
        {secretFrom(uri)}
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
