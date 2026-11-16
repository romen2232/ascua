import { useRouter } from "expo-router";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { session, useSession } from "../auth/session";
import { Button } from "../ui/Button";
import { ErrorText } from "../ui/ErrorText";
import { Screen } from "../ui/Screen";
import { TextField } from "../ui/TextField";

export function TotpScreen() {
  const { t } = useTranslation();
  const router = useRouter();
  const { status, error } = useSession();
  const [code, setCode] = useState("");

  useEffect(() => {
    if (status === "signed-in") router.replace("/");
    if (status === "signed-out") router.replace("/sign-in");
  }, [status, router]);

  return (
    <Screen title={t("auth.totp.title")}>
      <TextField
        label={t("auth.fields.code")}
        value={code}
        onChangeText={setCode}
        keyboardType="number-pad"
        autoComplete="one-time-code"
        maxLength={6}
      />
      <ErrorText code={error} />
      <Button label={t("auth.totp.submit")} onPress={() => session.verifyTotp(code)} disabled={code.length !== 6} />
    </Screen>
  );
}
