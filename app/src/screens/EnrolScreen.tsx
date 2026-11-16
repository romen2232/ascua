import { Redirect, useRouter } from "expo-router";

import { session, useSession } from "../auth/session";
import { TotpEnrolmentStep } from "./TotpEnrolmentStep";

/** Shown when a correct password belongs to an account that never finished TOTP set-up. */
export function EnrolScreen() {
  const router = useRouter();
  const { enrolment } = useSession();
  if (!enrolment) return <Redirect href="/sign-in" />;
  return (
    <TotpEnrolmentStep
      uri={enrolment.uri}
      enrolmentToken={enrolment.token}
      onConfirmed={() => {
        session.finishEnrolment();
        router.replace("/sign-in");
      }}
    />
  );
}
