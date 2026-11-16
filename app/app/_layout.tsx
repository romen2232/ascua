import "../src/i18n";

import { Stack } from "expo-router";
import { useEffect } from "react";

import { session } from "../src/auth/session";

export default function RootLayout() {
  useEffect(() => {
    void session.restore();
  }, []);
  return <Stack screenOptions={{ headerShown: false }} />;
}
