import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Link,
  NavLink,
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom";
import { isAxiosError } from "axios";
import toast from "react-hot-toast";
import { Button } from "../../../components/ui/Button";
import { Input } from "../../../components/ui/Input";
import { Card } from "../../../components/ui/Card";
import { useAuthStore } from "../../../store/authStore";
import {
  salesApi,
  orderPayload,
  saveBlob,
  sourceLabels,
  statusLabels,
  kindLabels,
  docLabels,
  type Customer,
  type Seller,
  type Order,
  type OrderPayload,
  type Details,
  type Source,
  type Kind,
  type DocType,
  type SalesDocument,
  type Totals,
} from "../../../api/sales";

const selectClass =
  "w-full rounded-xl border border-line bg-surface-raised px-3 py-2 text-sm text-content";
const today = () => new Date().toLocaleDateString("en-CA");
const fieldNames: Record<string, string> = {
  name: "Наименование / ФИО",
  kind: "Тип",
  phone: "Телефон",
  inn: "ИНН",
  email: "Email",
  kpp: "КПП",
  ogrn: "ОГРН / ОГРНИП",
  customer_id: "Покупатель",
  seller_id: "Организация-продавец",
  responsible_id: "Ответственный",
  order_date: "Дата заказа",
  delivery_address: "Адрес доставки",
  basis: "Основание передачи (договор / заказ)",
  vat_rules: "НДС по периодам",
  quantity: "Количество",
  price: "Цена",
  discount: "Скидка",
  vat_rate: "НДС",
  legal_address: "Юридический адрес / адрес физлица",
  account: "Расчётный счёт",
  bik: "БИК",
  correspondent_account: "Корреспондентский счёт",
};
interface ValidationIssue {
  loc: (string | number)[];
  msg: string;
  type: string;
}
function validationIssues(error: unknown): ValidationIssue[] {
  return isAxiosError(error) && Array.isArray(error.response?.data?.detail)
    ? error.response.data.detail
    : [];
}
function issueMessage(issue: ValidationIssue) {
  if (issue.type === "value_error")
    return issue.msg.replace(/^Value error, /, "");
  if (issue.type === "missing") return "Заполните обязательное поле";
  if (issue.type === "string_pattern_mismatch")
    return "Проверьте формат и число цифр";
  if (issue.type === "greater_than" || issue.type === "greater_than_equal")
    return "Укажите допустимое положительное значение";
  if (issue.type === "less_than_equal")
    return "Значение превышает допустимый предел";
  if (issue.type.startsWith("decimal"))
    return "Проверьте число и количество знаков после запятой";
  return "Проверьте введённое значение";
}
function errorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const d = error.response?.data?.detail;
    if (typeof d === "string") return d;
    if (d?.missing_fields) return d.missing_fields.join("\n");
    const issues = validationIssues(error);
    if (issues.length)
      return issues
        .map(
          (v) =>
            `${fieldNames[String(v.loc[v.loc.length - 1])] || "Поле формы"}: ${issueMessage(v)}`,
        )
        .join("\n");
  }
  return "Не удалось выполнить операцию. Проверьте соединение и повторите.";
}
const ValidationContext = createContext<ValidationIssue[]>([]);
function Field({ label, children }: { label: string; children: ReactNode }) {
  const errors = useContext(ValidationContext);
  const issue = errors.find(
    (e) =>
      label.replace(/ \*$/, "") === fieldNames[String(e.loc[e.loc.length - 1])],
  );
  return (
    <label className="block space-y-1 text-sm">
      <span className="text-content-muted">{label}</span>
      {children}
      {issue && (
        <span role="alert" className="block text-xs text-rose-600">
          {issueMessage(issue)}
        </span>
      )}
    </label>
  );
}
function Failure({ error }: { error: unknown }) {
  return error ? (
    <p
      role="alert"
      className="whitespace-pre-line rounded-xl bg-rose-500/10 p-3 text-sm text-rose-600"
    >
      {errorMessage(error)}
    </p>
  ) : null;
}
function Pager({
  total,
  offset,
  setOffset,
}: {
  total: number;
  offset: number;
  setOffset: (n: number) => void;
}) {
  return (
    <div className="flex items-center gap-3 py-4">
      <Button
        variant="secondary"
        disabled={!offset}
        onClick={() => setOffset(Math.max(0, offset - 20))}
      >
        Назад
      </Button>
      <span>
        {total
          ? `${offset + 1}–${Math.min(offset + 20, total)} из ${total}`
          : "Нет записей"}
      </span>
      <Button
        variant="secondary"
        disabled={offset + 20 >= total}
        onClick={() => setOffset(offset + 20)}
      >
        Далее
      </Button>
    </div>
  );
}
function useDebounce(value: string) {
  const [v, setV] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setV(value), 300);
    return () => clearTimeout(t);
  }, [value]);
  return v;
}

export function SalesPage() {
  const { pathname } = useLocation();
  const { id } = useParams();
  const section = pathname.split("/")[3] || "orders";
  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold">Продажи</h1>
      <nav aria-label="Продажи" className="flex flex-wrap gap-2">
        {[
          ["orders", "Заказы"],
          ["customers", "Клиенты"],
          ["documents", "Документы"],
          ["sellers", "Продавцы"],
        ].map(([key, text]) => (
          <NavLink
            key={key}
            to={`/app/sales/${key}`}
            className={({ isActive }) =>
              `rounded-xl px-4 py-2 ${isActive ? "bg-accent-soft text-accent" : "bg-surface-raised"}`
            }
          >
            {text}
          </NavLink>
        ))}
      </nav>
      {section === "customers" ? (
        <Customers id={id} />
      ) : section === "sellers" ? (
        <Sellers />
      ) : section === "documents" ? (
        <Documents />
      ) : id || pathname.endsWith("/new") ? (
        <OrderEditor id={id} key={id || "new"} />
      ) : (
        <Orders />
      )}
    </div>
  );
}

const detailFields: [string, string][] = [
  ["full_name", "Полное юридическое наименование"],
  ["email", "Email"],
  ["contact", "Контактное лицо"],
  ["telegram", "Telegram"],
  ["vk", "ВКонтакте"],
  ["kpp", "КПП"],
  ["ogrn", "ОГРН / ОГРНИП"],
  ["legal_address", "Юридический адрес / адрес физлица"],
  ["actual_address", "Фактический адрес"],
  ["shipping_address", "Адрес отгрузки"],
  ["account", "Расчётный счёт"],
  ["bank", "Банк"],
  ["bik", "БИК"],
  ["correspondent_account", "Корреспондентский счёт"],
  ["signatory", "ФИО подписанта"],
  ["position", "Должность подписанта"],
  ["authority", "Основание полномочий"],
  ["taxation", "Налоговый режим"],
  ["okpo", "ОКПО"],
  ["comment", "Комментарий"],
];
function PartyEditor({
  seller,
  value,
  onSaved,
  onClose,
}: {
  seller?: boolean;
  value?: Customer | Seller;
  onSaved: (p: Customer | Seller) => void;
  onClose: () => void;
}) {
  const user = useAuthStore((s) => s.user);
  const [name, setName] = useState(value?.name || "");
  const [kind, setKind] = useState<Kind>(
    value?.kind || (seller ? "ip" : "person"),
  );
  const [phone, setPhone] = useState((value as Customer)?.phone || "");
  const [inn, setInn] = useState(value?.inn || "");
  const [details, setDetails] = useState<Details>(value?.details || {});
  const [responsible, setResponsible] = useState(
    (value as Customer)?.responsible_id || user?.id || "",
  );
  const [active, setActive] = useState(
    seller
      ? ((value as Seller)?.active ?? true)
      : !(value as Customer)?.archived,
  );
  const [rules, setRules] = useState(
    (value as Seller)?.vat_rules || [
      { from_date: today(), to_date: null, rates: [null] },
    ],
  );
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const staff = useQuery({
    queryKey: ["sales-staff"],
    queryFn: salesApi.staff,
  });
  const change = (k: string, v: string | string[]) =>
    setDetails((prev) => ({ ...prev, [k]: v }));
  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const common = {
        name,
        kind,
        inn: inn || null,
        details: { ...details, email: details.email || null },
      };
      const payload = seller
        ? { ...common, active, vat_rules: rules }
        : {
            ...common,
            phone: phone || null,
            archived: !active,
            responsible_id: responsible || null,
          };
      const result = await salesApi.save<Customer | Seller>(
        seller ? "sellers" : "customers",
        payload,
        value?.id,
      );
      onSaved(result);
      toast.success("Сохранено");
      if (!seller && (result as Customer).duplicates?.length)
        toast(
          `Возможный дубль: ${(result as Customer).duplicates.map((d) => d.name).join(", ")}`,
          { icon: "⚠️", duration: 8000 },
        );
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Card>
      <ValidationContext.Provider value={validationIssues(error)}>
        <form className="space-y-4" onSubmit={submit}>
          <h2 className="text-lg font-semibold">
            {value ? "Редактирование" : "Новая карточка"}{" "}
            {seller ? "продавца" : "покупателя"}
          </h2>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <Field label="Тип">
              <select
                className={selectClass}
                value={kind}
                onChange={(e) => setKind(e.target.value as Kind)}
              >
                {Object.entries(kindLabels)
                  .filter(([k]) => !seller || k !== "person")
                  .map(([k, v]) => (
                    <option key={k} value={k}>
                      {v}
                    </option>
                  ))}
              </select>
            </Field>
            <Field label="Наименование / ФИО *">
              <Input
                required
                maxLength={255}
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </Field>
            <Field label="ИНН">
              <Input
                pattern={kind === "legal" ? "[0-9]{10}" : "[0-9]{12}"}
                value={inn}
                onChange={(e) => setInn(e.target.value)}
              />
            </Field>
            {!seller && (
              <>
                <Field label="Телефон">
                  <Input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                  />
                </Field>
                <Field label="Ответственный">
                  <select
                    className={selectClass}
                    value={responsible}
                    onChange={(e) => setResponsible(e.target.value)}
                  >
                    {staff.data?.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.name}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="Источник">
                  <select
                    className={selectClass}
                    value={String(details.source || "manual")}
                    onChange={(e) => change("source", e.target.value)}
                  >
                    {Object.entries(sourceLabels).map(([k, v]) => (
                      <option value={k} key={k}>
                        {v}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="Адреса доставки (по одному в строке)">
                  <textarea
                    className={selectClass}
                    value={
                      Array.isArray(details.delivery_addresses)
                        ? details.delivery_addresses.join("\n")
                        : ""
                    }
                    onChange={(e) =>
                      change(
                        "delivery_addresses",
                        e.target.value.split("\n").filter(Boolean),
                      )
                    }
                  />
                </Field>
              </>
            )}
            {detailFields
              .filter(([k]) =>
                seller
                  ? ![
                      "contact",
                      "telegram",
                      "vk",
                      "actual_address",
                      "comment",
                    ].includes(k)
                  : ![
                      "shipping_address",
                      "signatory",
                      "position",
                      "authority",
                      "taxation",
                      "okpo",
                      "okei",
                    ].includes(k),
              )
              .map(([key, label]) => (
                <Field key={key} label={label}>
                  <Input
                    type={key === "email" ? "email" : "text"}
                    value={String(details[key] || "")}
                    onChange={(e) => change(key, e.target.value)}
                  />
                </Field>
              ))}
          </div>
          <label className="flex gap-2">
            <input
              type="checkbox"
              checked={active}
              onChange={(e) => setActive(e.target.checked)}
            />
            {seller ? "Действующий продавец" : "Действующий покупатель"}
          </label>
          {seller && (
            <section className="space-y-3">
              <h3 className="font-semibold">НДС по периодам</h3>
              <p className="text-sm text-content-muted">
                Укажите применимые ставки через запятую: например, 22, 10, 0.
                Для освобождения напишите «без». Проверьте ставки с бухгалтером.
              </p>
              {rules.map((r, n) => (
                <div className="grid items-end gap-3 md:grid-cols-4" key={n}>
                  <Field label="С даты">
                    <Input
                      type="date"
                      required
                      value={r.from_date}
                      onChange={(e) =>
                        setRules(
                          rules.map((v, i) =>
                            i === n ? { ...v, from_date: e.target.value } : v,
                          ),
                        )
                      }
                    />
                  </Field>
                  <Field label="По дату">
                    <Input
                      type="date"
                      value={r.to_date || ""}
                      onChange={(e) =>
                        setRules(
                          rules.map((v, i) =>
                            i === n
                              ? { ...v, to_date: e.target.value || null }
                              : v,
                          ),
                        )
                      }
                    />
                  </Field>
                  <Field label="Разрешённые ставки">
                    <Input
                      key={JSON.stringify(r)}
                      defaultValue={r.rates.map((v) => v ?? "без").join(", ")}
                      onBlur={(e) =>
                        setRules(
                          rules.map((v, i) =>
                            i === n
                              ? {
                                  ...v,
                                  rates: e.target.value
                                    .split(",")
                                    .map((s) =>
                                      s.trim().toLowerCase() === "без"
                                        ? null
                                        : s.trim(),
                                    ),
                                }
                              : v,
                          ),
                        )
                      }
                    />
                  </Field>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => setRules(rules.filter((_, i) => i !== n))}
                  >
                    Удалить период
                  </Button>
                </div>
              ))}
              <Button
                type="button"
                variant="secondary"
                onClick={() =>
                  setRules([
                    ...rules,
                    { from_date: today(), to_date: null, rates: [null] },
                  ])
                }
              >
                Добавить период
              </Button>
            </section>
          )}
          <Failure error={error} />
          <div className="flex gap-3">
            <Button disabled={busy} type="submit">
              {busy ? "Сохранение…" : "Сохранить"}
            </Button>
            <Button type="button" variant="secondary" onClick={onClose}>
              Закрыть
            </Button>
          </div>
        </form>
      </ValidationContext.Provider>
    </Card>
  );
}

function Customers({ id }: { id?: string }) {
  const [q, setQ] = useState("");
  const dq = useDebounce(q);
  const [kind, setKind] = useState("");
  const [archived, setArchived] = useState(false);
  const [offset, setOffset] = useState(0);
  const [edit, setEdit] = useState<Customer | null | undefined>();
  const cache = useQueryClient();
  const list = useQuery({
    queryKey: ["sales-customers", dq, kind, archived, offset],
    queryFn: () =>
      salesApi.list<Customer>("customers", {
        q: dq,
        kind: kind || undefined,
        archived,
        offset,
      }),
    enabled: !id,
  });
  const card = useQuery({
    queryKey: ["sales-customer", id],
    queryFn: () => salesApi.get<Customer>("customers", id!),
    enabled: !!id,
  });
  const history = useQuery({
    queryKey: ["sales-customer-orders", id, offset],
    queryFn: () => salesApi.list<Order>(`customers/${id}/orders`, { offset }),
    enabled: !!id,
  });
  async function archive(c: Customer) {
    if (!confirm(`Архивировать покупателя «${c.name}»? История сохранится.`))
      return;
    try {
      await salesApi.save(
        "customers",
        {
          kind: c.kind,
          name: c.name,
          phone: c.phone,
          inn: c.inn,
          details: c.details,
          responsible_id: c.responsible_id,
          archived: true,
        },
        c.id,
      );
      await cache.invalidateQueries({ queryKey: ["sales-customers"] });
    } catch (e) {
      toast.error(errorMessage(e));
    }
  }
  return (
    <div className="space-y-4">
      {edit !== undefined && (
        <PartyEditor
          value={edit || undefined}
          onSaved={() => {
            setEdit(undefined);
            void cache.invalidateQueries({ queryKey: ["sales-customers"] });
            if (id) void card.refetch();
          }}
          onClose={() => setEdit(undefined)}
        />
      )}
      {id ? (
        <>
          <Failure error={card.error} />
          {card.isLoading && <p>Загрузка…</p>}
          {card.data && (
            <Card>
              <h2 className="text-xl font-semibold">{card.data.name}</h2>
              <p>
                {kindLabels[card.data.kind]} · {card.data.phone} · ИНН{" "}
                {card.data.inn || "не указан"}
              </p>
              <p>{String(card.data.details.legal_address || "")}</p>
              <p>{String(card.data.details.comment || "")}</p>
              <Button onClick={() => setEdit(card.data)}>Редактировать</Button>
            </Card>
          )}
          <h3>История заказов</h3>
          <Failure error={history.error} />
          <OrderTable orders={history.data?.items || []} />
          <Pager
            total={history.data?.total || 0}
            offset={offset}
            setOffset={setOffset}
          />
        </>
      ) : (
        <>
          <div className="flex flex-wrap items-center gap-3">
            <div className="min-w-60 flex-1">
              <Input
                aria-label="Поиск клиентов"
                placeholder="ФИО, название, телефон, ИНН"
                value={q}
                onChange={(e) => {
                  setQ(e.target.value);
                  setOffset(0);
                }}
              />
            </div>
            <select
              aria-label="Тип покупателя"
              className={selectClass + " max-w-60"}
              value={kind}
              onChange={(e) => {
                setKind(e.target.value);
                setOffset(0);
              }}
            >
              <option value="">Все типы</option>
              {Object.entries(kindLabels).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
            <label className="flex gap-2">
              <input
                type="checkbox"
                checked={archived}
                onChange={(e) => {
                  setArchived(e.target.checked);
                  setOffset(0);
                }}
              />
              Архив
            </label>
            <Button onClick={() => setEdit(null)}>Добавить клиента</Button>
          </div>
          <Failure error={list.error} />
          {list.isLoading ? (
            <p>Загрузка…</p>
          ) : (
            <Card>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr>
                      {[
                        "Покупатель",
                        "Тип",
                        "Телефон",
                        "ИНН",
                        "Источник",
                        "Заказы",
                        "Последний заказ",
                        "Действия",
                      ].map((v) => (
                        <th className="p-3" key={v}>
                          {v}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {list.data?.items.map((c) => (
                      <tr className="border-t border-line" key={c.id}>
                        <td className="p-3">
                          <Link
                            className="text-accent"
                            to={`/app/sales/customers/${c.id}`}
                          >
                            {c.name}
                          </Link>
                          {c.duplicates.length > 0 && (
                            <p className="text-amber-600">
                              Возможный дубль:{" "}
                              {c.duplicates.map((d) => d.name).join(", ")}
                            </p>
                          )}
                        </td>
                        <td className="p-3">{kindLabels[c.kind]}</td>
                        <td>{c.phone}</td>
                        <td>{c.inn}</td>
                        <td>
                          {
                            sourceLabels[
                              (c.details.source as Source) || "manual"
                            ]
                          }
                        </td>
                        <td>{c.orders_count}</td>
                        <td>{c.last_order || "—"}</td>
                        <td className="space-x-2">
                          <Button
                            variant="secondary"
                            onClick={() => setEdit(c)}
                          >
                            Изменить
                          </Button>
                          {!c.archived && (
                            <Button
                              variant="secondary"
                              onClick={() => void archive(c)}
                            >
                              В архив
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {list.data?.total === 0 && (
                  <p className="p-4">
                    Покупателей пока нет. Добавьте первого клиента.
                  </p>
                )}
              </div>
              <Pager
                total={list.data?.total || 0}
                offset={offset}
                setOffset={setOffset}
              />
            </Card>
          )}
        </>
      )}
    </div>
  );
}

function Sellers() {
  const [edit, setEdit] = useState<Seller | null | undefined>();
  const [offset, setOffset] = useState(0);
  const cache = useQueryClient();
  const user = useAuthStore((s) => s.user);
  const admin = ["company_admin", "superadmin"].includes(user?.role || "");
  const list = useQuery({
    queryKey: ["sales-sellers", offset],
    queryFn: () => salesApi.list<Seller>("sellers", { limit: 20, offset }),
  });
  return (
    <div className="space-y-4">
      <Failure error={list.error} />
      {admin && (
        <Button onClick={() => setEdit(null)}>Добавить продавца</Button>
      )}
      {edit !== undefined && (
        <PartyEditor
          seller
          value={edit || undefined}
          onSaved={() => {
            setEdit(undefined);
            void cache.invalidateQueries({ queryKey: ["sales-sellers"] });
          }}
          onClose={() => setEdit(undefined)}
        />
      )}
      {list.isLoading && <p>Загрузка…</p>}
      <div className="grid gap-4 md:grid-cols-2">
        {list.data?.items.map((s) => (
          <Card key={s.id}>
            <h2 className="font-semibold">{s.name}</h2>
            <p>
              ИНН {s.inn || "не указан"} ·{" "}
              {s.active ? "Действующий" : "Неактивен"}
            </p>
            <p>{String(s.details.legal_address || "")}</p>
            {admin && (
              <Button variant="secondary" onClick={() => setEdit(s)}>
                Редактировать реквизиты и НДС
              </Button>
            )}
          </Card>
        ))}
      </div>
      {list.data?.total === 0 && (
        <p>
          Добавьте организацию-продавца и настройки НДС перед созданием заказов.
        </p>
      )}
      <Pager
        total={list.data?.total || 0}
        offset={offset}
        setOffset={setOffset}
      />
    </div>
  );
}

function OrderTable({ orders }: { orders: Order[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr>
            {[
              "Номер / дата",
              "Продавец",
              "Покупатель",
              "Источник",
              "Позиций",
              "Сумма",
              "Статус",
              "Ответственный",
            ].map((v) => (
              <th key={v} className="p-3">
                {v}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id} className="border-t border-line">
              <td className="p-3">
                <Link
                  className="text-accent break-all"
                  to={`/app/sales/orders/${o.id}`}
                >
                  {o.number}
                </Link>
                <p>{o.order_date}</p>
              </td>
              <td className="p-3">{o.seller_name}</td>
              <td>{o.customer_name}</td>
              <td>{sourceLabels[o.source]}</td>
              <td>{o.items.length}</td>
              <td className="whitespace-nowrap">{o.total} ₽</td>
              <td>{statusLabels[o.status]}</td>
              <td>{o.responsible_name}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {!orders.length && <p className="p-4">Заказов не найдено.</p>}
    </div>
  );
}
function Orders() {
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [offset, setOffset] = useState(0);
  const list = useQuery({
    queryKey: ["sales-orders", filters, offset],
    queryFn: () =>
      salesApi.list<Order>("orders", {
        ...Object.fromEntries(
          Object.entries(filters).filter(
            ([k, v]) => v && k !== "customer_search",
          ),
        ),
        offset,
      }),
  });
  const sellers = useQuery({
    queryKey: ["sales-sellers"],
    queryFn: () => salesApi.list<Seller>("sellers"),
  });
  const staff = useQuery({
    queryKey: ["sales-staff"],
    queryFn: salesApi.staff,
  });
  const customerQ = useDebounce(filters.customer_search || "");
  const customers = useQuery({
    queryKey: ["sales-customer-search", customerQ],
    queryFn: () => salesApi.list<Customer>("customers", { q: customerQ }),
  });
  function filter(k: string, v: string) {
    setOffset(0);
    setFilters((f) => ({ ...f, [k]: v }));
  }
  return (
    <div className="space-y-4">
      <Link to="/app/sales/orders/new">
        <Button>Новый заказ</Button>
      </Link>
      <Card>
        <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-4">
          <Field label="Номер / покупатель">
            <Input
              value={filters.q || ""}
              onChange={(e) => filter("q", e.target.value)}
            />
          </Field>
          <Field label="С даты">
            <Input
              type="date"
              onChange={(e) => filter("from_date", e.target.value)}
            />
          </Field>
          <Field label="По дату">
            <Input
              type="date"
              onChange={(e) => filter("to_date", e.target.value)}
            />
          </Field>
          <Field label="Статус">
            <select
              className={selectClass}
              onChange={(e) => filter("status", e.target.value)}
            >
              <option value="">Все</option>
              {Object.entries(statusLabels).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Продавец">
            <select
              className={selectClass}
              onChange={(e) => filter("seller_id", e.target.value)}
            >
              <option value="">Все</option>
              {sellers.data?.items.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Источник">
            <select
              className={selectClass}
              onChange={(e) => filter("source", e.target.value)}
            >
              <option value="">Все</option>
              {Object.entries(sourceLabels).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Ответственный">
            <select
              className={selectClass}
              onChange={(e) => filter("responsible_id", e.target.value)}
            >
              <option value="">Все</option>
              {staff.data?.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Поиск покупателя">
            <Input
              onChange={(e) => filter("customer_search", e.target.value)}
            />
            <select
              aria-label="Покупатель"
              className={selectClass}
              value={filters.customer_id || ""}
              onChange={(e) => filter("customer_id", e.target.value)}
            >
              <option value="">Все покупатели</option>
              {customers.data?.items.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </Field>
        </div>
      </Card>
      <Failure error={list.error} />
      {list.isLoading ? (
        <p>Загрузка…</p>
      ) : (
        <Card>
          <OrderTable orders={list.data?.items || []} />
          <Pager
            total={list.data?.total || 0}
            offset={offset}
            setOffset={setOffset}
          />
        </Card>
      )}
    </div>
  );
}

function OrderEditor({ id }: { id?: string }) {
  const user = useAuthStore((s) => s.user);
  const manager = ["manager", "company_admin", "superadmin"].includes(
    user?.role || "",
  );
  const navigate = useNavigate();
  const cache = useQueryClient();
  const [form, setForm] = useState<OrderPayload>({
    customer_id: "",
    seller_id: "",
    responsible_id: user?.id || null,
    order_date: today(),
    source: "manual",
    delivery_address: "",
    comment: "",
    basis: "",
    vat_included: true,
    items: [],
  });
  const [busy, setBusy] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [newCustomer, setNewCustomer] = useState(false);
  const [tab, setTab] = useState("items");
  const [customerQ, setCustomerQ] = useState("");
  const dc = useDebounce(customerQ);
  const [productQ, setProductQ] = useState("");
  const dp = useDebounce(productQ);
  const order = useQuery({
    queryKey: ["sales-order", id],
    queryFn: () => salesApi.get<Order>("orders", id!),
    enabled: !!id,
  });
  const sellers = useQuery({
    queryKey: ["sales-sellers"],
    queryFn: () => salesApi.list<Seller>("sellers"),
  });
  const customers = useQuery({
    queryKey: ["sales-customer-search", dc],
    queryFn: () => salesApi.list<Customer>("customers", { q: dc }),
  });
  const selectedCustomer = useQuery({
    queryKey: ["sales-customer", form.customer_id],
    queryFn: () => salesApi.get<Customer>("customers", form.customer_id),
    enabled: !!form.customer_id,
  });
  const staff = useQuery({
    queryKey: ["sales-staff"],
    queryFn: salesApi.staff,
  });
  const catalog = useQuery({
    queryKey: ["sales-catalog", dp],
    queryFn: () => salesApi.catalog(dp),
    enabled: tab === "items",
  });
  const history = useQuery({
    queryKey: ["sales-history", id],
    queryFn: () => salesApi.history(id!),
    enabled: !!id && tab === "history",
  });
  const initialLoaded = useRef(false);
  useEffect(() => {
    if (order.data && !initialLoaded.current) {
      setForm(order.data);
      initialLoaded.current = true;
    }
  }, [order.data]);
  const editable = !id || order.data?.status === "draft";
  function change<K extends keyof OrderPayload>(
    key: K,
    value: OrderPayload[K],
  ) {
    setForm((f) => ({ ...f, [key]: value }));
    setDirty(true);
  }
  const calculationKey = useDebounce(JSON.stringify(orderPayload(form)));
  const calculationPayload = JSON.parse(calculationKey) as OrderPayload;
  const calculation = useQuery({
    queryKey: ["sales-calculation", calculationKey],
    queryFn: () => salesApi.calculate(calculationPayload),
    enabled:
      !!calculationPayload.seller_id &&
      !!calculationPayload.customer_id &&
      editable,
    retry: false,
  });
  const totals: Totals | undefined = editable
    ? calculation.data
    : order.data
      ? {
          total: order.data.total,
          vat_total: order.data.vat_total,
          discount_total: order.data.discount_total,
          lines: order.data.items.map((i) => ({
            total: i.total || "0",
            vat_amount: i.vat_amount || "0",
          })),
        }
      : undefined;
  const seller = sellers.data?.items.find((s) => s.id === form.seller_id);
  const rates =
    seller?.vat_rules.find(
      (r) =>
        r.from_date <= form.order_date &&
        (!r.to_date || r.to_date >= form.order_date),
    )?.rates || [];
  async function save(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const saved = await salesApi.save<Order>(
        "orders",
        orderPayload(form),
        id,
      );
      setForm(saved);
      setDirty(false);
      await cache.invalidateQueries({ queryKey: ["sales-orders"] });
      if (!id) navigate(`/app/sales/orders/${saved.id}`);
      else await order.refetch();
      toast.success("Заказ сохранён");
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  async function action(action: string) {
    if (!id) return;
    if (
      ["cancel", "complete", "reopen"].includes(action) &&
      !confirm(
        action === "cancel"
          ? "Отменить заказ?"
          : action === "reopen"
            ? "Вернуть заказ в черновик? Выпущенные документы сохранятся."
            : "Завершить заказ вручную? Это не фиксирует складскую отгрузку.",
      )
    )
      return;
    setBusy(true);
    setError(null);
    try {
      const result = await salesApi.action(id, action);
      if (action === "duplicate") navigate(`/app/sales/orders/${result.id}`);
      else {
        setForm(result);
        setDirty(false);
        await order.refetch();
        void cache.invalidateQueries({ queryKey: ["sales-history", id] });
      }
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  if (id && order.isLoading) return <p>Загрузка заказа…</p>;
  if (id && order.error) return <Failure error={order.error} />;
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <h2 className="text-xl font-semibold break-all">
          {order.data?.number || "Новый заказ"}
        </h2>
        <span className="rounded-lg bg-accent-soft px-3 py-1 text-accent">
          {order.data ? statusLabels[order.data.status] : "Черновик"}
        </span>
        {id && (
          <Button
            disabled={busy || dirty}
            variant="secondary"
            onClick={() => void action("duplicate")}
          >
            Повторить заказ
          </Button>
        )}
        {manager && id && order.data?.status === "draft" && (
          <Button
            disabled={busy || dirty}
            onClick={() => void action("confirm")}
          >
            Подтвердить
          </Button>
        )}
        {manager && order.data?.status === "confirmed" && (
          <>
            <Button disabled={busy} onClick={() => void action("complete")}>
              Завершить вручную
            </Button>
            <Button
              disabled={busy}
              variant="secondary"
              onClick={() => void action("reopen")}
            >
              Вернуть в черновик
            </Button>
          </>
        )}
        {manager &&
          id &&
          ["draft", "confirmed"].includes(order.data?.status || "") && (
            <Button
              disabled={busy || dirty}
              variant="danger"
              onClick={() => void action("cancel")}
            >
              Отменить заказ
            </Button>
          )}
      </div>
      <Failure error={error} />
      {dirty && (
        <p className="text-amber-600">
          Есть несохранённые изменения. Сохраните заказ перед подтверждением.
        </p>
      )}
      {newCustomer && (
        <PartyEditor
          onClose={() => setNewCustomer(false)}
          onSaved={(p) => {
            change("customer_id", p.id);
            setCustomerQ(p.name);
            setNewCustomer(false);
            void cache.invalidateQueries({
              queryKey: ["sales-customer-search"],
            });
          }}
        />
      )}
      <ValidationContext.Provider value={validationIssues(error)}>
        <form onSubmit={save} className="space-y-4">
          <Card>
            <fieldset
              disabled={!editable || busy}
              className="grid gap-4 md:grid-cols-2 xl:grid-cols-3"
            >
              <Field label="Организация-продавец *">
                <select
                  required
                  className={selectClass}
                  value={form.seller_id}
                  onChange={(e) => change("seller_id", e.target.value)}
                >
                  <option value="">Выберите продавца</option>
                  {sellers.data?.items
                    .filter((s) => s.active || s.id === form.seller_id)
                    .map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name}
                      </option>
                    ))}
                </select>
                <Link className="text-accent text-xs" to="/app/sales/sellers">
                  Реквизиты и ставки НДС
                </Link>
              </Field>
              <Field label="Покупатель *">
                <Input
                  aria-label="Поиск покупателя"
                  placeholder="Поиск по имени, телефону, ИНН"
                  value={customerQ}
                  onChange={(e) => setCustomerQ(e.target.value)}
                />
                <select
                  required
                  className={selectClass}
                  value={form.customer_id}
                  onChange={(e) => {
                    change("customer_id", e.target.value);
                    const c = customers.data?.items.find(
                      (c) => c.id === e.target.value,
                    );
                    const addresses = c?.details.delivery_addresses;
                    if (Array.isArray(addresses) && addresses[0])
                      change("delivery_address", addresses[0]);
                  }}
                >
                  <option value="">Выберите покупателя</option>
                  {form.customer_id &&
                    !customers.data?.items.some(
                      (c) => c.id === form.customer_id,
                    ) && (
                      <option value={form.customer_id}>
                        {order.data?.customer_name || "Выбранный покупатель"}
                      </option>
                    )}
                  {customers.data?.items.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} {c.inn}
                    </option>
                  ))}
                </select>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setNewCustomer(true)}
                >
                  Быстро добавить клиента
                </Button>
              </Field>
              <Field label="Дата заказа *">
                <Input
                  required
                  type="date"
                  value={form.order_date}
                  onChange={(e) => change("order_date", e.target.value)}
                />
              </Field>
              <Field label="Источник">
                <select
                  className={selectClass}
                  value={form.source}
                  onChange={(e) => change("source", e.target.value as Source)}
                >
                  {Object.entries(sourceLabels).map(([k, v]) => (
                    <option key={k} value={k}>
                      {v}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label="Ответственный">
                <select
                  className={selectClass}
                  value={form.responsible_id || ""}
                  onChange={(e) => change("responsible_id", e.target.value)}
                >
                  {staff.data?.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label="Адрес доставки">
                <Input
                  list="delivery-addresses"
                  value={form.delivery_address}
                  onChange={(e) => change("delivery_address", e.target.value)}
                />
                <datalist id="delivery-addresses">
                  {(
                    (selectedCustomer.data?.details
                      .delivery_addresses as string[]) || []
                  ).map((a) => (
                    <option key={a} value={a} />
                  ))}
                </datalist>
              </Field>
              <Field label="Основание передачи (договор / заказ)">
                <Input
                  value={form.basis}
                  onChange={(e) => change("basis", e.target.value)}
                />
              </Field>
              <Field label="Комментарий">
                <textarea
                  className={selectClass}
                  value={form.comment}
                  onChange={(e) => change("comment", e.target.value)}
                />
              </Field>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={form.vat_included}
                  onChange={(e) => change("vat_included", e.target.checked)}
                />
                Цены включают НДС
              </label>
            </fieldset>
            <Failure error={sellers.error || customers.error || staff.error} />
          </Card>
          <div role="tablist" className="flex gap-2">
            {[
              ["items", "Товары"],
              ["documents", "Документы"],
              ["history", "История"],
            ].map(([k, v]) => (
              <Button
                role="tab"
                aria-selected={tab === k}
                variant={tab === k ? "primary" : "secondary"}
                type="button"
                key={k}
                onClick={() => setTab(k)}
              >
                {v}
              </Button>
            ))}
          </div>
          {tab === "items" && (
            <Card>
              {editable && (
                <div className="mb-4 space-y-2">
                  <Input
                    aria-label="Поиск товара"
                    placeholder="Название, артикул или GTIN"
                    value={productQ}
                    onChange={(e) => setProductQ(e.target.value)}
                  />
                  <Failure error={catalog.error} />
                  {catalog.isLoading && <p>Поиск товаров…</p>}
                  <div className="max-h-44 overflow-y-auto">
                    {catalog.data?.items.map((p) => (
                      <button
                        type="button"
                        key={p.id}
                        className="block w-full rounded-lg p-2 text-left hover:bg-surface-overlay"
                        onClick={() => {
                          change("items", [
                            ...form.items,
                            {
                              product_id: p.id,
                              name: p.name,
                              article: p.article,
                              gtin: p.gtin,
                              unit: "шт.",
                              okei: "796",
                              quantity: "1",
                              price: "0.00",
                              discount: "0",
                              vat_rate: rates[0] ?? null,
                            },
                          ]);
                          setProductQ("");
                        }}
                      >
                        {p.name} · {p.article || "без артикула"} ·{" "}
                        {p.gtin || "без GTIN"}{" "}
                        <span className="text-accent">Добавить</span>
                      </button>
                    ))}
                    {catalog.data?.total === 0 && (
                      <p>Товар не найден в каталоге.</p>
                    )}
                  </div>
                </div>
              )}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr>
                      {[
                        "Товар",
                        "Кол-во",
                        "Ед.",
                        "ОКЕИ",
                        "Цена",
                        "Скидка %",
                        "НДС",
                        "Сумма",
                        "",
                      ].map((v, i) => (
                        <th className="p-2" key={i}>
                          {v}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {form.items.map((line, n) => (
                      <tr className="border-t border-line" key={n}>
                        <td className="p-2 min-w-48">
                          {line.name}
                          <p className="text-xs text-content-muted">
                            {line.article} · {line.gtin}
                          </p>
                        </td>
                        {(
                          [
                            "quantity",
                            "unit",
                            "okei",
                            "price",
                            "discount",
                          ] as const
                        ).map((k) => (
                          <td className="p-2 min-w-24" key={k}>
                            <Input
                              aria-label={`${k === "quantity" ? "Количество" : k === "unit" ? "Единица измерения" : k === "okei" ? "ОКЕИ" : k === "price" ? "Цена" : "Скидка"} позиции ${n + 1}`}
                              disabled={!editable}
                              required
                              type={
                                k === "unit" || k === "okei" ? "text" : "number"
                              }
                              min={k === "quantity" ? "0.001" : "0"}
                              max={k === "discount" ? 100 : undefined}
                              step={
                                k === "quantity"
                                  ? ".001"
                                  : k === "discount"
                                    ? ".0001"
                                    : ".01"
                              }
                              value={line[k] || ""}
                              onChange={(e) =>
                                change(
                                  "items",
                                  form.items.map((v, i) =>
                                    i === n ? { ...v, [k]: e.target.value } : v,
                                  ),
                                )
                              }
                            />
                          </td>
                        ))}
                        <td className="p-2 min-w-28">
                          <select
                            aria-label={`НДС позиции ${n + 1}`}
                            className={selectClass}
                            disabled={!editable}
                            value={line.vat_rate ?? "none"}
                            onChange={(e) =>
                              change(
                                "items",
                                form.items.map((v, i) =>
                                  i === n
                                    ? {
                                        ...v,
                                        vat_rate:
                                          e.target.value === "none"
                                            ? null
                                            : e.target.value,
                                      }
                                    : v,
                                ),
                              )
                            }
                          >
                            {[...new Set([...rates, line.vat_rate])].map(
                              (r) => (
                                <option key={r ?? "none"} value={r ?? "none"}>
                                  {r === null ? "Без НДС" : `${r}%`}
                                </option>
                              ),
                            )}
                          </select>
                        </td>
                        <td className="p-2 whitespace-nowrap">
                          {totals?.lines[n]?.total || "—"} ₽
                        </td>
                        <td>
                          {editable && (
                            <Button
                              type="button"
                              variant="secondary"
                              aria-label={`Удалить позицию ${n + 1}`}
                              onClick={() =>
                                change(
                                  "items",
                                  form.items.filter((_, i) => i !== n),
                                )
                              }
                            >
                              Удалить
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {!form.items.length && (
                  <p className="p-4">Добавьте товары из каталога.</p>
                )}
              </div>
              <Failure error={editable ? calculation.error : null} />
              <div className="mt-4 flex flex-wrap gap-6 border-t border-line pt-4">
                <p>Скидка: {totals?.discount_total || "—"} ₽</p>
                <p>НДС: {totals?.vat_total || "—"} ₽</p>
                <p className="font-bold">
                  К оплате: {totals?.total || "—"} ₽{" "}
                  {calculation.isFetching && " · Расчёт…"}
                </p>
              </div>
            </Card>
          )}
          {editable && (
            <Button type="submit" disabled={busy}>
              {busy ? "Сохранение…" : "Сохранить черновик"}
            </Button>
          )}
        </form>
      </ValidationContext.Provider>
      {tab === "documents" &&
        (id ? (
          <Documents
            orderId={id}
            status={order.data?.status}
            dirty={dirty}
            revision={order.data?.revision}
          />
        ) : (
          <p>Сохраните заказ для предварительного просмотра документов.</p>
        ))}
      {tab === "history" && (
        <Card>
          <Failure error={history.error} />
          {history.isLoading && <p>Загрузка…</p>}
          {history.data?.map((h) => (
            <p className="border-b border-line py-3" key={h.id}>
              {new Date(h.created_at).toLocaleString("ru-RU")} ·{" "}
              {staff.data?.find((u) => u.id === h.user_id)?.name || "Сотрудник"}{" "}
              ·{" "}
              {(
                {
                  "sales.order.create": "Заказ создан",
                  "sales.order.update": "Черновик изменён",
                  "sales.order.confirmed": "Заказ подтверждён",
                  "sales.order.completed": "Завершён вручную",
                  "sales.order.cancelled": "Заказ отменён",
                  "sales.order.draft": "Возвращён в черновик",
                  "sales.order.document": "Документ выпущен",
                } as Record<string, string>
              )[h.action] || "Изменение заказа"}
              {h.meta_json.version ? ` · версия ${h.meta_json.version}` : ""}
            </p>
          ))}
          {!history.data?.length && (
            <p>История появится после сохранения заказа.</p>
          )}
        </Card>
      )}
    </div>
  );
}

function Documents({
  orderId,
  status,
  dirty,
  revision,
}: {
  orderId?: string;
  status?: Order["status"];
  dirty?: boolean;
  revision?: number;
}) {
  const [offset, setOffset] = useState(0);
  const [type, setType] = useState<DocType>("torg12");
  const [date, setDate] = useState(today());
  const [updStatus, setUpdStatus] = useState(2);
  const [newVersion, setNewVersion] = useState(false);
  const [templateId, setTemplateId] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const cache = useQueryClient();
  const user = useAuthStore((s) => s.user);
  const manager = ["manager", "company_admin", "superadmin"].includes(
    user?.role || "",
  );
  const list = useQuery({
    queryKey: ["sales-documents", orderId, offset],
    queryFn: () =>
      salesApi.list<SalesDocument>(
        orderId ? `orders/${orderId}/documents` : "documents",
        { offset },
      ),
  });
  const templates = useQuery({
    queryKey: ["sales-templates"],
    queryFn: salesApi.templates,
    enabled: !!orderId,
  });
  const key = useRef(crypto.randomUUID());
  useEffect(() => {
    key.current = crypto.randomUUID();
  }, [type, date, updStatus, newVersion, templateId, revision]);
  useEffect(
    () => () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    },
    [previewUrl],
  );
  async function generate(preview: boolean) {
    if (!orderId) return;
    setBusy(true);
    setError(null);
    try {
      const payload = {
        document_type: type,
        document_date: date,
        upd_status: updStatus,
        template_id: templateId || null,
      };
      if (preview) {
        const blob = await salesApi.preview(orderId, {
          ...payload,
          format: "pdf",
        });
        setPreviewUrl(URL.createObjectURL(blob));
      } else {
        if (
          newVersion &&
          !confirm(
            "Выпустить новую версию? Предыдущие документы останутся в истории.",
          )
        )
          return;
        await salesApi.issue(orderId, {
          ...payload,
          idempotency_key: key.current,
          new_version: newVersion,
        });
        await cache.invalidateQueries({ queryKey: ["sales-documents"] });
        void cache.invalidateQueries({ queryKey: ["sales-history", orderId] });
        setNewVersion(false);
        toast.success("Excel и PDF сохранены в истории");
      }
    } catch (e) {
      if (isAxiosError(e) && e.response?.data instanceof Blob) {
        try {
          const body = JSON.parse(await e.response.data.text());
          setError({ response: { data: body }, isAxiosError: true });
        } catch {
          setError(e);
        }
      } else setError(e);
    } finally {
      setBusy(false);
    }
  }
  async function download(d: SalesDocument, format: "xlsx" | "pdf") {
    try {
      const blob = await salesApi.download(d.id, format);
      saveBlob(
        blob,
        `${d.document_type}-${d.year}-${d.number}-v${d.version}.${format}`,
      );
    } catch (e) {
      toast.error(errorMessage(e));
    }
  }
  return (
    <div className="space-y-4">
      {orderId && (
        <Card>
          <h3 className="mb-3 font-semibold">Формирование документа</h3>
          <p className="mb-4 text-sm text-content-muted">
            Стартовые печатные формы требуют бухгалтерской проверки. Выпуск
            документа сохраняет файлы; фактическая отгрузка оформляется
            отдельно.
          </p>
          <div className="grid gap-3 md:grid-cols-3">
            <Field label="Вид документа">
              <select
                className={selectClass}
                value={type}
                onChange={(e) => {
                  setType(e.target.value as DocType);
                  setTemplateId("");
                }}
              >
                {Object.entries(docLabels).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Дата документа">
              <Input
                type="date"
                required
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </Field>
            <Field label="Шаблон">
              <select
                className={selectClass}
                value={templateId}
                onChange={(e) => setTemplateId(e.target.value)}
              >
                <option value="">Актуальный шаблон</option>
                {templates.data
                  ?.filter((t) => t.document_type === type)
                  .map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name} · v{t.version}
                    </option>
                  ))}
              </select>
            </Field>
            {type === "upd" && (
              <Field label="Статус УПД">
                <select
                  className={selectClass}
                  value={updStatus}
                  onChange={(e) => setUpdStatus(Number(e.target.value))}
                >
                  <option value={2}>2 — передаточный документ</option>
                  <option value={1}>1 — счёт-фактура и передача</option>
                </select>
              </Field>
            )}
          </div>
          {manager && (
            <label className="my-4 flex gap-2">
              <input
                type="checkbox"
                checked={newVersion}
                onChange={(e) => setNewVersion(e.target.checked)}
              />
              Выпустить новую версию с сохранением предыдущей
            </label>
          )}
          <div className="mt-4 flex flex-wrap gap-3">
            <Button
              variant="secondary"
              disabled={busy || dirty || !date}
              onClick={() => void generate(true)}
            >
              Предпросмотр с пометкой «Черновик»
            </Button>
            <Button
              disabled={
                busy ||
                dirty ||
                !date ||
                !["confirmed", "completed"].includes(status || "")
              }
              onClick={() => void generate(false)}
            >
              {busy ? "Формирование…" : "Сформировать Excel и PDF"}
            </Button>
          </div>
          {!["confirmed", "completed"].includes(status || "") && (
            <p className="mt-2 text-sm text-content-muted">
              Для выпуска подтвердите заказ.
            </p>
          )}
          <Failure error={error || templates.error} />
          {previewUrl && (
            <>
              <a
                href={previewUrl}
                target="_blank"
                rel="noreferrer"
                className="block py-3 text-accent"
              >
                Открыть черновик в отдельной вкладке
              </a>
              <iframe
                title="Предварительный просмотр документа"
                src={previewUrl}
                className="h-[600px] w-full rounded-xl border border-line"
              />
            </>
          )}
        </Card>
      )}
      <Failure error={list.error} />
      {list.isLoading ? (
        <p>Загрузка документов…</p>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr>
                  {["Документ", "Дата", "Версия", "Заказ", "Скачать"].map(
                    (v) => (
                      <th className="p-3" key={v}>
                        {v}
                      </th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody>
                {list.data?.items.map((d) => (
                  <tr key={d.id} className="border-t border-line">
                    <td className="p-3">
                      {docLabels[d.document_type]} № {d.number}/{d.year}
                    </td>
                    <td>{d.document_date}</td>
                    <td>{d.version}</td>
                    <td>
                      <Link
                        className="text-accent"
                        to={`/app/sales/orders/${d.order_id}`}
                      >
                        Открыть заказ
                      </Link>
                    </td>
                    <td className="flex gap-2 p-3">
                      <Button
                        variant="secondary"
                        onClick={() => void download(d, "xlsx")}
                      >
                        Excel
                      </Button>
                      <Button
                        variant="secondary"
                        onClick={() => void download(d, "pdf")}
                      >
                        PDF
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {list.data?.total === 0 && (
              <p className="p-4">Выпущенных документов пока нет.</p>
            )}
          </div>
          <Pager
            total={list.data?.total || 0}
            offset={offset}
            setOffset={setOffset}
          />
        </Card>
      )}
    </div>
  );
}
