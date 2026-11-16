import { Redirect, Stack } from "expo-router";
import { ActivityIndicator, View } from "react-native";

import { useSession } from "../../src/auth/session";

export default function SignedInLayout() {
  const { status } = useSession();
  if (status === "loading") {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
        <ActivityIndicator />
      </View>
    );
  }
  if (status !== "signed-in") return <Redirect href="/sign-in" />;
  return <Stack screenOptions={{ headerShown: false }} />;
}
