import { useTranslation } from "react-i18next";
import { Text } from "react-native";

import { useSession } from "../auth/session";
import { Button } from "../ui/Button";
import { Screen } from "../ui/Screen";

export function HomeScreen() {
  const { t } = useTranslation();
  const { user, signOut } = useSession();
  return (
    <Screen title={t("home.welcome", { name: user?.display_name ?? "" })}>
      <Text>{t("home.empty")}</Text>
      <Button label={t("home.signOut")} variant="secondary" onPress={() => void signOut()} />
    </Screen>
  );
}
