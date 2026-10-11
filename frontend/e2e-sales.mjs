/** Real browser/API workflow. Requires an isolated seeded backend; no network mocks. */
import { chromium } from "playwright";
import assert from "node:assert/strict";
import { mkdir, writeFile } from "node:fs/promises";
const base = process.env.SALES_TEST_BASE_URL || "http://127.0.0.1:55173";
if (!/^http:\/\/(127\.0\.0\.1|localhost):\d+$/.test(base))
  throw new Error("Use a local isolated test server");
const output = new URL("../output/sales/", import.meta.url);
await mkdir(output, { recursive: true });
const browser = await chromium.launch({
  headless: true,
  ...(process.env.SALES_TEST_BROWSER_PATH
    ? { executablePath: process.env.SALES_TEST_BROWSER_PATH }
    : {}),
});
try {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1100 },
  });
  const suffix = Date.now().toString().slice(-6);
  const sellerName = `ИП Иванова ${suffix}`;
  const customerName = `Петрова Мария ${suffix}`;
  const errors = [];
  const failedResponses = [];
  page.on("response", (r) => {
    if (r.status() >= 400 && r.url().includes("/api/"))
      failedResponses.push(`${r.status()} ${r.url()}`);
  });
  page.on("pageerror", (e) => errors.push(e.message));
  await page.addInitScript(() => {
    if (window.top === window)
      localStorage.setItem(
        "prostomark-theme",
        JSON.stringify({ state: { preference: "light" }, version: 0 }),
      );
  });
  await page.goto(`${base}/login`);
  await page
    .getByPlaceholder("Email", { exact: true })
    .fill("sales-test@example.com");
  await page.getByPlaceholder("Пароль").fill("SalesTestOnly123!");
  await page.getByRole("button", { name: "Войти", exact: true }).click();
  await page.waitForURL("**/app/dashboard");
  await page.goto(`${base}/app/sales/sellers`);
  await page
    .getByRole("button", { name: "Добавить продавца", exact: true })
    .click();
  await page
    .getByLabel("Наименование / ФИО *", { exact: true })
    .fill(sellerName);
  await page.getByLabel("ИНН", { exact: true }).fill("123456789012");
  await page
    .getByLabel("Полное юридическое наименование", { exact: true })
    .fill("ИП Иванова Анна Сергеевна");
  await page
    .getByLabel("Юридический адрес / адрес физлица", { exact: true })
    .fill("Москва, улица Примерная, дом 1");
  await page.getByLabel("ФИО подписанта").fill("Иванова Анна Сергеевна");
  await page
    .getByLabel("Должность подписанта")
    .fill("Индивидуальный предприниматель");
  await page.getByLabel("Основание полномочий").fill("Регистрация ИП");
  await page.getByLabel("С даты", { exact: true }).fill("2026-01-01");
  await page.getByLabel("Разрешённые ставки").fill("22, без");
  await page.getByLabel("Разрешённые ставки").blur();
  await page.getByRole("button", { name: "Сохранить", exact: true }).click();
  await page.getByRole("heading", { name: sellerName, exact: true }).waitFor();
  await page.goto(`${base}/app/sales/customers`);
  await page
    .getByRole("button", { name: "Добавить клиента", exact: true })
    .click();
  await page
    .getByLabel("Наименование / ФИО *", { exact: true })
    .fill(customerName);
  await page.getByLabel("Телефон", { exact: true }).fill("+7 900 111-22-33");
  await page
    .getByLabel("Юридический адрес / адрес физлица", { exact: true })
    .fill("Москва, улица Покупателей, дом 2");
  await page
    .getByLabel("Адреса доставки (по одному в строке)")
    .fill("Москва, улица Покупателей, дом 2");
  await page.getByRole("button", { name: "Сохранить", exact: true }).click();
  await page.getByRole("link", { name: customerName, exact: true }).waitFor();
  await page.screenshot({
    path: new URL("customers.png", output).pathname,
    fullPage: true,
  });
  await page.goto(`${base}/app/sales/orders/new`);
  await page
    .getByLabel("Организация-продавец *")
    .selectOption({ label: sellerName });
  await page
    .locator("label")
    .filter({ hasText: "Покупатель *" })
    .locator("select")
    .selectOption({ label: customerName });
  await page.getByLabel("Дата заказа *").fill("2026-10-11");
  await page
    .getByLabel("Основание передачи (договор / заказ)")
    .fill("Заказ покупателя № 1");
  await page
    .getByRole("button", { name: /Крем увлажняющий 50 мл.*Добавить/ })
    .click();
  await page.getByLabel("Количество позиции 1").fill("2");
  await page.getByLabel("Цена позиции 1").fill("122");
  await page.getByLabel("НДС позиции 1").selectOption("22");
  await page.getByText("К оплате: 244.00 ₽", { exact: false }).waitFor();
  await page
    .getByRole("button", { name: "Сохранить черновик", exact: true })
    .click();
  await page.waitForURL(/\/app\/sales\/orders\/[0-9a-f-]{36}$/);
  const orderUrl = page.url();
  await page.reload();
  await page.getByLabel("Цена позиции 1").waitFor();
  assert.equal(await page.getByLabel("Цена позиции 1").inputValue(), "122.00");
  await page.getByRole("button", { name: "Подтвердить", exact: true }).click();
  await page.getByText("Подтверждён", { exact: true }).waitFor();
  assert.equal(await page.getByRole("alert").count(), 0);
  await page.screenshot({
    path: new URL("order.png", output).pathname,
    fullPage: true,
  });
  await page.getByRole("tab", { name: "Документы", exact: true }).click();
  await page
    .getByRole("button", { name: "Предпросмотр с пометкой «Черновик»" })
    .click();
  await page.getByTitle("Предварительный просмотр документа").waitFor();
  await page
    .getByRole("button", { name: "Сформировать Excel и PDF", exact: true })
    .click();
  await page.getByRole("button", { name: "Excel", exact: true }).waitFor();
  const [xlsx] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: "Excel", exact: true }).click(),
  ]);
  await xlsx.saveAs(new URL("torg12.xlsx", output).pathname);
  const [pdf] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: "PDF", exact: true }).click(),
  ]);
  await pdf.saveAs(new URL("torg12.pdf", output).pathname);
  await page.screenshot({
    path: new URL("documents.png", output).pathname,
    fullPage: true,
  });
  await page.goto(`${base}/app/sales/orders`);
  await page.getByRole("link", { name: /^З-/ }).first().waitFor();
  await page.screenshot({
    path: new URL("orders.png", output).pathname,
    fullPage: true,
  });
  await page.evaluate(() => document.documentElement.classList.add("dark"));
  await page.screenshot({
    path: new URL("orders-dark.png", output).pathname,
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(orderUrl);
  await page.getByText("Подтверждён", { exact: true }).waitFor();
  await page.screenshot({
    path: new URL("order-mobile.png", output).pathname,
    fullPage: true,
  });
  assert.deepEqual(errors, []);
  assert.deepEqual(failedResponses, []);
  await writeFile(
    new URL("browser-results.json", output),
    JSON.stringify(
      {
        passed: true,
        workflow:
          "login → seller → customer → order → reload → confirm → preview → XLSX/PDF download",
        screenshots: 6,
        consoleErrors: errors,
      },
      null,
      2,
    ),
  );
  console.log(
    "Sales browser workflow passed; screenshots and actual downloaded files in output/sales",
  );
} finally {
  await browser.close();
}
