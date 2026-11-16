import { useRouter } from "expo-router";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { session, useSession } from "../auth/session";
import { Button } from "../ui/Button";
import { ErrorText } from "../ui/ErrorText";
import { Screen } from "../ui/Screen";
import { TextField } from "../ui/TextField";

export function SignInScreen() {
  const { t } = useTranslation();
  const router = useRouter();
  const { error } = useSession();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    setBusy(true);
    await session.signIn(email, password);
    setBusy(false);
    const { status } = session.getState();
    if (status === "mfa") router.push("/totp");
    if (status === "enrol") router.push("/enrol");
  };

  return (
    <Screen title={t("auth.signIn.title")}>
      <TextField
        label={t("auth.fields.email")}
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        autoComplete="email"
        keyboardType="email-address"
      />
      <TextField
        label={t("auth.fields.password")}
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        autoComplete="current-password"
      />
      <ErrorText code={error} />
      <Button label={t("auth.signIn.submit")} onPress={submit} disabled={busy} />
    </Screen>
  );
}
