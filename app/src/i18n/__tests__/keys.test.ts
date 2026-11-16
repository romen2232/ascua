import en from "../en.json";
import es from "../es.json";

function keys(obj: object, prefix = ""): string[] {
  return Object.entries(obj).flatMap(([k, v]) =>
    typeof v === "object" && v !== null ? keys(v, `${prefix}${k}.`) : [`${prefix}${k}`],
  );
}

it("es.json and en.json have identical key sets", () => {
  expect(keys(es).sort()).toEqual(keys(en).sort());
});

it("no translation is empty", () => {
  const empty = (obj: object): boolean =>
    Object.values(obj).some((v) => (typeof v === "object" ? empty(v) : v === ""));
  expect(empty(es) || empty(en)).toBe(false);
});
