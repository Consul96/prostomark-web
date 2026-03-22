import { type ReactNode } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  Binary,
  Bot,
  Boxes,
  Building2,
  CheckCircle2,
  ChevronRight,
  Factory,
  Layers3,
  MessageSquareText,
  PackageCheck,
  Radar,
  ScanLine,
  Send,
  Settings2,
  ShieldCheck,
  Sparkles,
  Store,
  Truck,
  Waypoints,
} from 'lucide-react';
import { Link } from 'react-router-dom';

const navigationItems = [
  { label: 'Услуги', href: '#services' },
  { label: 'Решения', href: '#solutions' },
  { label: 'Кейсы', href: '#results' },
  { label: 'О нас', href: '#process' },
  { label: 'Контакты', href: '#cta' },
];

const heroBadges = ['1С / ERP / WMS', 'API интеграции', 'AI и автоматизация'];

const segmentCards = [
  {
    title: 'Импортеры',
    description: 'Собираем стабильный поток данных между поставщиками, 1С и контуром маркировки без ручных переносов.',
    pain: 'Сложные интеграции и длительный запуск.',
    icon: Building2,
  },
  {
    title: 'Производители',
    description: 'Автоматизируем выпуск, агрегацию и контроль КМ на уровне производственной цепочки.',
    pain: 'Ошибки в маркировке и непрозрачный production flow.',
    icon: Factory,
  },
  {
    title: 'Логистика',
    description: 'Связываем WMS, сканирование, отгрузки и статусы, чтобы команды видели движение товара в реальном времени.',
    pain: 'Потеря статусов и разрывы между складами.',
    icon: Truck,
  },
  {
    title: 'Оптовые компании',
    description: 'Убираем ручные операции в документообороте, актах и передаче кодов между контрагентами.',
    pain: 'Ручные процессы и накопление операционного долга.',
    icon: Boxes,
  },
  {
    title: 'Маркетплейсы',
    description: 'Настраиваем обмен данными с площадками, фидами, API и внутренними сервисами без хаоса.',
    pain: 'Долгий запуск и отсутствие единого слоя управления.',
    icon: Store,
  },
];

const serviceCards = [
  {
    title: 'Внедрение Честного Знака',
    description: 'Проектируем архитектуру маркировки, статусы, обмены и контроль ошибок на каждом этапе.',
    icon: ShieldCheck,
  },
  {
    title: 'Интеграции с 1С / API',
    description: 'Соединяем ERP, WMS, сайты, маркетплейсы и внутренние сервисы в единый поток данных.',
    icon: Waypoints,
  },
  {
    title: 'Автоматизация процессов',
    description: 'Убираем повторяющиеся операции, сокращаем ручной труд и проектируем измеримый workflow.',
    icon: Settings2,
  },
  {
    title: 'AI и чат-боты',
    description: 'Подключаем AI-ассистентов, классификацию документов, подсказки командам и Telegram-ботов.',
    icon: Bot,
  },
  {
    title: 'Поддержка и сопровождение',
    description: 'Следим за стабильностью процессов, SLA, логами, алертами и развитием внедрённых решений.',
    icon: Radar,
  },
  {
    title: 'Разработка внутренних сервисов',
    description: 'Создаём dashboard-интерфейсы, кабинеты, middleware и сервисы под сложные операционные процессы.',
    icon: Layers3,
  },
];

const processSteps = [
  { title: 'Аудит', description: 'Карта процессов, рисков и ограничений интеграции.' },
  { title: 'Проектирование', description: 'Архитектура, роли, данные и контрольные точки.' },
  { title: 'Разработка', description: 'Сервисы, интерфейсы, API и сценарии автоматизации.' },
  { title: 'Интеграция', description: 'Подключение 1С, ERP, WMS и внешних контуров.' },
  { title: 'Поддержка', description: 'Мониторинг, развитие и операционная устойчивость.' },
];

const metricCards = [
  { value: '70%', label: 'меньше ручных операций', detail: 'Рутины уходят в сценарии, триггеры и проверки данных.' },
  { value: '2-3x', label: 'быстрее запуск процессов', detail: 'От пилота до production без потери контроля качества.' },
  { value: '99%', label: 'снижение ошибок данных', detail: 'Валидации и сверки встроены в сам поток обработки.' },
  { value: '100%', label: 'контроль статусов', detail: 'Команды видят жизненный цикл товара и документа в одном контуре.' },
];

const aiCapabilities = [
  'Анализ документов и классификация входящих пакетов',
  'Обработка фото, этикеток и визуальный контроль маркировки',
  'Интеллектуальные подсказки сотрудникам по статусам и ошибкам',
  'AI-ассистенты и Telegram-боты для операционных команд',
];

const footerLinks = [
  { label: 'Услуги', href: '#services' },
  { label: 'Решения', href: '#solutions' },
  { label: 'Кейсы', href: '#results' },
  { label: 'Контакты', href: '#cta' },
];

const heroPanels = [
  {
    title: 'Заявка #202146',
    subtitle: 'Новая партия / импорт',
    accent: 'from-cyan-400/70 via-sky-500/40 to-blue-500/30',
    className: 'left-[8%] top-[12%] w-[52%] -rotate-6',
    icon: ScanLine,
  },
  {
    title: 'Статус: КМ нанесены',
    subtitle: 'Поток синхронизирован',
    accent: 'from-blue-400/70 via-cyan-400/40 to-violet-500/30',
    className: 'right-[4%] top-[10%] w-[44%] rotate-3',
    icon: CheckCircle2,
  },
  {
    title: 'AI Анализ',
    subtitle: 'Ошибок в потоке: 0.2%',
    accent: 'from-violet-400/70 via-blue-500/45 to-cyan-400/25',
    className: 'right-[2%] top-[35%] w-[48%] -rotate-2',
    icon: Sparkles,
  },
  {
    title: 'Интеграция',
    subtitle: '1С / API / Маркетплейсы',
    accent: 'from-cyan-400/60 via-blue-500/45 to-slate-200/10',
    className: 'left-[22%] bottom-[20%] w-[42%] rotate-2',
    icon: Waypoints,
  },
  {
    title: 'Контур данных',
    subtitle: 'ERP / WMS / API gateway',
    accent: 'from-sky-400/60 via-blue-500/30 to-violet-500/25',
    className: 'right-[8%] bottom-[10%] w-[46%] rotate-1',
    icon: Binary,
  },
];

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 },
};

const fadeIn = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
};

function SectionHeading({
  eyebrow,
  title,
  description,
  align = 'left',
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: 'left' | 'center';
}) {
  return (
    <div className={align === 'center' ? 'mx-auto max-w-3xl text-center' : 'max-w-3xl'}>
      {eyebrow ? (
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.28em] text-cyan-200/80 backdrop-blur">
          <span className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_16px_rgba(34,211,238,0.85)]" />
          {eyebrow}
        </div>
      ) : null}
      <h2 className="text-3xl font-bold tracking-tight text-slate-50 md:text-4xl">{title}</h2>
      {description ? <p className="mt-4 text-base leading-7 text-slate-300 md:text-lg">{description}</p> : null}
    </div>
  );
}

function SectionShell({
  id,
  children,
  className = '',
}: {
  id?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section id={id} className={`relative py-16 md:py-24 ${className}`}>
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">{children}</div>
    </section>
  );
}

function MetricChip({ label }: { label: string }) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.06] px-3 py-2 text-xs font-medium text-slate-200 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)] backdrop-blur">
      <span className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_14px_rgba(34,211,238,0.8)]" />
      {label}
    </div>
  );
}

function GridCard({
  icon: Icon,
  title,
  description,
  footer,
}: {
  icon: typeof Building2;
  title: string;
  description: string;
  footer: string;
}) {
  return (
    <motion.article
      variants={fadeInUp}
      className="group relative overflow-hidden rounded-[28px] border border-white/10 bg-white/[0.05] p-5 shadow-[0_20px_80px_-45px_rgba(59,130,246,0.45)] backdrop-blur-xl transition duration-500 hover:-translate-y-1 hover:border-cyan-300/30 hover:bg-white/[0.07]"
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(56,189,248,0.14),transparent_35%),radial-gradient(circle_at_bottom_left,rgba(139,92,246,0.12),transparent_40%)] opacity-80 transition duration-500 group-hover:opacity-100" />
      <div className="absolute right-0 top-0 h-24 w-24 bg-[linear-gradient(135deg,rgba(255,255,255,0.16),transparent_65%)] opacity-40" />
      <div className="relative">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-slate-950/50 text-cyan-200 shadow-[0_0_30px_rgba(59,130,246,0.18)]">
          <Icon className="h-5 w-5" />
        </div>
        <h3 className="mt-5 text-xl font-semibold text-slate-50">{title}</h3>
        <p className="mt-3 text-sm leading-6 text-slate-300">{description}</p>
        <p className="mt-5 border-t border-white/10 pt-4 text-sm text-slate-400">{footer}</p>
      </div>
    </motion.article>
  );
}

function ServiceCard({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof Building2;
  title: string;
  description: string;
}) {
  return (
    <motion.article
      variants={fadeInUp}
      className="group relative overflow-hidden rounded-[30px] border border-white/10 bg-[linear-gradient(180deg,rgba(15,23,42,0.84),rgba(15,23,42,0.62))] p-[1px] shadow-[0_24px_80px_-50px_rgba(6,182,212,0.45)]"
    >
      <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(59,130,246,0.35),transparent_35%,transparent_65%,rgba(139,92,246,0.2))] opacity-50 transition duration-500 group-hover:opacity-100" />
      <div className="relative h-full rounded-[29px] border border-white/8 bg-[radial-gradient(circle_at_top,rgba(59,130,246,0.12),transparent_35%),linear-gradient(180deg,rgba(9,14,28,0.95),rgba(12,19,36,0.84))] p-6 backdrop-blur-xl transition duration-500 group-hover:-translate-y-1 group-hover:border-cyan-300/20">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-300/20 bg-cyan-400/10 text-cyan-200">
          <Icon className="h-5 w-5" />
        </div>
        <h3 className="mt-5 text-xl font-semibold text-slate-50">{title}</h3>
        <p className="mt-3 text-sm leading-6 text-slate-300">{description}</p>
        <div className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-cyan-200">
          Подробнее
          <ChevronRight className="h-4 w-4 transition duration-300 group-hover:translate-x-1" />
        </div>
      </div>
    </motion.article>
  );
}

function HeroPanel({
  title,
  subtitle,
  accent,
  className,
  icon: Icon,
}: {
  title: string;
  subtitle: string;
  accent: string;
  className: string;
  icon: typeof Building2;
}) {
  return (
    <motion.div
      variants={fadeInUp}
      className={`absolute rounded-[24px] border border-white/15 bg-slate-950/55 p-[1px] shadow-[0_30px_100px_-45px_rgba(14,165,233,0.65)] backdrop-blur-2xl ${className}`}
    >
      <div className="relative overflow-hidden rounded-[23px] border border-white/10 bg-[linear-gradient(180deg,rgba(15,23,42,0.94),rgba(15,23,42,0.72))] px-5 py-4">
        <div className={`absolute inset-0 bg-gradient-to-r ${accent} opacity-20`} />
        <div className="absolute inset-x-6 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/80 to-transparent" />
        <div className="relative flex items-start gap-4">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/10 text-cyan-200">
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <div className="text-base font-semibold text-slate-50">{title}</div>
            <div className="mt-1 text-sm text-slate-300">{subtitle}</div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function HomePage() {
  return (
    <div className="relative overflow-hidden bg-[#070b16] text-slate-100">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute inset-0 bg-[linear-gradient(rgba(148,163,184,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.06)_1px,transparent_1px)] bg-[size:72px_72px] opacity-20" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.2),transparent_30%),radial-gradient(circle_at_top_right,rgba(6,182,212,0.18),transparent_28%),radial-gradient(circle_at_50%_60%,rgba(139,92,246,0.12),transparent_32%),linear-gradient(180deg,#0b1020_0%,#09111f_45%,#070b16_100%)]" />
        <motion.div
          className="absolute -left-24 top-20 h-80 w-80 rounded-full bg-blue-500/20 blur-[120px]"
          animate={{ x: [0, 30, -10, 0], y: [0, 25, -15, 0] }}
          transition={{ duration: 18, repeat: Number.POSITIVE_INFINITY, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute right-0 top-1/3 h-[30rem] w-[30rem] rounded-full bg-cyan-400/15 blur-[140px]"
          animate={{ x: [0, -35, 10, 0], y: [0, -20, 20, 0] }}
          transition={{ duration: 22, repeat: Number.POSITIVE_INFINITY, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute bottom-10 left-1/3 h-72 w-72 rounded-full bg-violet-500/12 blur-[120px]"
          animate={{ scale: [1, 1.08, 0.95, 1] }}
          transition={{ duration: 16, repeat: Number.POSITIVE_INFINITY, ease: 'easeInOut' }}
        />
      </div>

      <header className="sticky top-0 z-40 border-b border-white/10 bg-slate-950/35 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex min-w-0 items-center gap-4">
            <Link to="/" className="flex items-center gap-3">
              <div className="relative flex h-11 w-11 items-center justify-center overflow-hidden rounded-2xl border border-white/10 bg-[linear-gradient(135deg,rgba(56,189,248,0.24),rgba(59,130,246,0.08))] text-cyan-100 shadow-[0_10px_30px_-15px_rgba(14,165,233,0.65)]">
                <PackageCheck className="h-5 w-5" />
                <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(255,255,255,0.18),transparent_45%)]" />
              </div>
              <div className="min-w-0">
                <div className="text-sm font-semibold uppercase tracking-[0.26em] text-slate-300">Prime Trace</div>
                <div className="text-lg font-bold tracking-tight text-white">Честный Знак</div>
              </div>
            </Link>
            <div className="hidden text-sm text-slate-400 xl:block">Разработка • Консалтинг • Автоматизация</div>
          </div>

          <nav className="hidden items-center gap-7 text-sm text-slate-300 lg:flex">
            {navigationItems.map((item) => (
              <a key={item.label} href={item.href} className="transition hover:text-white">
                {item.label}
              </a>
            ))}
          </nav>

          <div className="hidden items-center gap-4 xl:flex">
            <a href="https://t.me/company" className="text-sm text-slate-300 transition hover:text-white">
              Telegram
            </a>
            <a href="mailto:hello@company.ru" className="text-sm text-slate-300 transition hover:text-white">
              hello@company.ru
            </a>
          </div>

          <Link
            to="/register"
            className="inline-flex items-center gap-2 rounded-2xl border border-cyan-300/20 bg-[linear-gradient(135deg,rgba(34,211,238,0.24),rgba(59,130,246,0.22))] px-5 py-3 text-sm font-semibold text-white shadow-[0_18px_40px_-20px_rgba(34,211,238,0.85)] transition hover:border-cyan-200/40 hover:shadow-[0_24px_60px_-24px_rgba(59,130,246,0.95)]"
          >
            Заказать аудит
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </header>

      <main className="relative z-10">
        <SectionShell className="overflow-hidden pb-10 pt-10 md:pb-16 md:pt-16">
          <div className="grid items-center gap-12 lg:grid-cols-[1.05fr_0.95fr] lg:gap-10">
            <motion.div
              initial="hidden"
              animate="visible"
              variants={fadeInUp}
              transition={{ duration: 0.7, ease: 'easeOut' }}
              className="relative"
            >
              <div className="inline-flex items-center gap-2 rounded-full border border-cyan-300/15 bg-cyan-300/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-cyan-100">
                <span className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_16px_rgba(34,211,238,0.85)]" />
                Enterprise automation for marked goods
              </div>

              <h1 className="mt-8 max-w-3xl text-5xl font-bold tracking-[-0.04em] text-white sm:text-6xl xl:text-7xl">
                Автоматизация Честного Знака и интеграций для бизнеса
              </h1>

              <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300 md:text-xl">
                Разрабатываем цифровые решения, внедряем интеграции и AI-инструменты для производителей, импортеров,
                логистики и e-commerce.
              </p>

              <div className="mt-10 flex flex-col gap-4 sm:flex-row">
                <Link
                  to="/register"
                  className="inline-flex items-center justify-center gap-2 rounded-2xl border border-cyan-300/25 bg-[linear-gradient(135deg,rgba(34,211,238,0.28),rgba(59,130,246,0.28))] px-6 py-4 text-sm font-semibold text-white shadow-[0_20px_45px_-20px_rgba(34,211,238,0.9)] transition hover:-translate-y-0.5 hover:shadow-[0_24px_55px_-20px_rgba(59,130,246,0.85)]"
                >
                  Обсудить проект
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <a
                  href="#solutions"
                  className="inline-flex items-center justify-center gap-2 rounded-2xl border border-white/12 bg-white/[0.04] px-6 py-4 text-sm font-semibold text-slate-100 backdrop-blur transition hover:border-white/20 hover:bg-white/[0.08]"
                >
                  Посмотреть решения
                </a>
              </div>

              <div className="mt-8 flex flex-wrap gap-3">
                {heroBadges.map((badge) => (
                  <MetricChip key={badge} label={badge} />
                ))}
              </div>
            </motion.div>

            <motion.div
              initial="hidden"
              animate="visible"
              variants={fadeIn}
              transition={{ duration: 0.8, ease: 'easeOut', delay: 0.15 }}
              className="relative mx-auto h-[34rem] w-full max-w-[42rem] lg:h-[40rem]"
            >
              <div className="absolute inset-0 rounded-[36px] border border-white/10 bg-[radial-gradient(circle_at_20%_10%,rgba(14,165,233,0.18),transparent_26%),radial-gradient(circle_at_75%_20%,rgba(139,92,246,0.18),transparent_24%),linear-gradient(180deg,rgba(9,14,28,0.92),rgba(7,11,22,0.78))] shadow-[0_50px_120px_-60px_rgba(59,130,246,0.8)]" />
              <div className="absolute inset-5 rounded-[30px] border border-white/8 bg-[linear-gradient(180deg,rgba(11,16,32,0.82),rgba(10,17,34,0.46))] backdrop-blur-2xl" />
              <div className="absolute inset-10 overflow-hidden rounded-[24px] border border-white/8 bg-[radial-gradient(circle_at_center,rgba(8,47,73,0.45),transparent_55%),linear-gradient(180deg,rgba(9,15,29,0.9),rgba(7,11,22,0.72))]">
                <div className="absolute inset-0 bg-[linear-gradient(rgba(59,130,246,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(59,130,246,0.08)_1px,transparent_1px)] bg-[size:32px_32px] opacity-80" />
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_15%,rgba(34,211,238,0.2),transparent_28%),radial-gradient(circle_at_10%_90%,rgba(139,92,246,0.18),transparent_22%),radial-gradient(circle_at_95%_65%,rgba(59,130,246,0.2),transparent_26%)]" />

                <motion.div
                  className="absolute left-[-6%] top-[56%] h-px w-[70%] bg-gradient-to-r from-transparent via-cyan-300/70 to-transparent"
                  animate={{ x: ['0%', '18%', '0%'], opacity: [0.55, 1, 0.55] }}
                  transition={{ duration: 8, repeat: Number.POSITIVE_INFINITY, ease: 'easeInOut' }}
                />
                <motion.div
                  className="absolute right-[-10%] top-[30%] h-px w-[62%] bg-gradient-to-r from-transparent via-violet-300/80 to-transparent"
                  animate={{ x: ['0%', '-16%', '0%'], opacity: [0.45, 0.95, 0.45] }}
                  transition={{ duration: 10, repeat: Number.POSITIVE_INFINITY, ease: 'easeInOut' }}
                />
                <motion.div
                  className="absolute bottom-[18%] left-[12%] h-[22rem] w-[22rem] rounded-full border border-cyan-300/15"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 28, repeat: Number.POSITIVE_INFINITY, ease: 'linear' }}
                />
                <motion.div
                  className="absolute bottom-[24%] left-[18%] h-[14rem] w-[14rem] rounded-full border border-violet-300/10"
                  animate={{ rotate: -360 }}
                  transition={{ duration: 18, repeat: Number.POSITIVE_INFINITY, ease: 'linear' }}
                />

                <div className="absolute left-[18%] top-[14%] h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_22px_rgba(34,211,238,1)]" />
                <div className="absolute left-[44%] top-[42%] h-2 w-2 rounded-full bg-blue-300 shadow-[0_0_22px_rgba(96,165,250,1)]" />
                <div className="absolute left-[70%] top-[22%] h-2 w-2 rounded-full bg-violet-300 shadow-[0_0_22px_rgba(196,181,253,1)]" />
                <div className="absolute bottom-[16%] right-[18%] h-2 w-2 rounded-full bg-cyan-200 shadow-[0_0_22px_rgba(165,243,252,1)]" />

                {heroPanels.map((panel, index) => (
                  <motion.div
                    key={panel.title}
                    initial="hidden"
                    animate="visible"
                    variants={fadeInUp}
                    transition={{ duration: 0.7, delay: 0.18 + index * 0.08, ease: 'easeOut' }}
                  >
                    <HeroPanel {...panel} />
                  </motion.div>
                ))}

                <div className="absolute inset-x-[10%] bottom-[7%] flex items-center justify-between rounded-[20px] border border-white/10 bg-slate-950/50 px-4 py-3 backdrop-blur">
                  <div>
                    <div className="text-xs uppercase tracking-[0.24em] text-slate-400">Data flow</div>
                    <div className="mt-1 text-sm font-medium text-slate-100">Очередь документов и кодов синхронизирована</div>
                  </div>
                  <div className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-200">
                    Stable
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </SectionShell>

        <SectionShell id="solutions" className="pt-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={fadeInUp}
            transition={{ duration: 0.7, ease: 'easeOut' }}
          >
            <SectionHeading
              eyebrow="Business segments"
              title="Решения для бизнеса"
              description="Собираем прозрачный и управляемый контур маркировки вокруг реальных операционных задач, а не вокруг отдельных модулей."
            />
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.15 }}
            transition={{ staggerChildren: 0.08 }}
            className="mt-10 grid gap-4 md:grid-cols-2 xl:grid-cols-5"
          >
            {segmentCards.map((segment) => (
              <GridCard
                key={segment.title}
                icon={segment.icon}
                title={segment.title}
                description={segment.description}
                footer={segment.pain}
              />
            ))}
          </motion.div>
        </SectionShell>

        <SectionShell id="services">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={fadeInUp}
            transition={{ duration: 0.7, ease: 'easeOut' }}
          >
            <SectionHeading
              eyebrow="Services"
              title="Наши услуги"
              description="От аудита и архитектуры до запуска production-сервисов и стабильного сопровождения в enterprise-среде."
            />
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.15 }}
            transition={{ staggerChildren: 0.08 }}
            className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-3"
          >
            {serviceCards.map((service) => (
              <ServiceCard key={service.title} icon={service.icon} title={service.title} description={service.description} />
            ))}
          </motion.div>
        </SectionShell>

        <SectionShell id="process">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={fadeInUp}
            transition={{ duration: 0.7, ease: 'easeOut' }}
          >
            <SectionHeading
              eyebrow="Process"
              title="Как мы работаем"
              description="Последовательно строим систему: от диагностики текущих узких мест до устойчивого production-контура с прозрачными статусами."
            />
          </motion.div>

          <div className="mt-12 overflow-hidden rounded-[32px] border border-white/10 bg-white/[0.04] p-6 shadow-[0_30px_100px_-55px_rgba(59,130,246,0.5)] backdrop-blur-xl md:p-8">
            <div className="relative hidden items-center justify-between gap-3 lg:flex">
              <div className="absolute left-10 right-10 top-10 h-px bg-gradient-to-r from-cyan-400/0 via-cyan-300/65 to-violet-400/0" />
              {processSteps.map((step, index) => (
                <motion.div
                  key={step.title}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, amount: 0.4 }}
                  variants={fadeInUp}
                  transition={{ duration: 0.55, delay: index * 0.08, ease: 'easeOut' }}
                  className="relative z-10 flex-1"
                >
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border border-cyan-300/20 bg-slate-950/80 text-sm font-semibold text-cyan-100 shadow-[0_0_30px_rgba(34,211,238,0.18)]">
                    0{index + 1}
                  </div>
                  <div className="mt-6 rounded-[24px] border border-white/10 bg-slate-950/45 p-5">
                    <h3 className="text-lg font-semibold text-white">{step.title}</h3>
                    <p className="mt-3 text-sm leading-6 text-slate-300">{step.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            <div className="grid gap-4 lg:hidden">
              {processSteps.map((step, index) => (
                <motion.div
                  key={step.title}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, amount: 0.3 }}
                  variants={fadeInUp}
                  transition={{ duration: 0.55, delay: index * 0.06, ease: 'easeOut' }}
                  className="rounded-[24px] border border-white/10 bg-slate-950/45 p-5"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex h-11 w-11 items-center justify-center rounded-full border border-cyan-300/20 bg-cyan-400/10 text-sm font-semibold text-cyan-100">
                      0{index + 1}
                    </div>
                    <h3 className="text-lg font-semibold text-white">{step.title}</h3>
                  </div>
                  <p className="mt-4 text-sm leading-6 text-slate-300">{step.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </SectionShell>

        <SectionShell id="results">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={fadeInUp}
            transition={{ duration: 0.7, ease: 'easeOut' }}
          >
            <SectionHeading
              eyebrow="Impact"
              title="Результаты для бизнеса"
              description="Проектируем решения так, чтобы бизнес видел не только внедрение, но и конкретный операционный эффект."
            />
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.15 }}
            transition={{ staggerChildren: 0.08 }}
            className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-4"
          >
            {metricCards.map((metric) => (
              <motion.article
                key={metric.value}
                variants={fadeInUp}
                className="relative overflow-hidden rounded-[30px] border border-white/10 bg-[linear-gradient(180deg,rgba(15,23,42,0.92),rgba(15,23,42,0.7))] p-7 shadow-[0_24px_80px_-54px_rgba(56,189,248,0.8)]"
              >
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(56,189,248,0.14),transparent_32%),radial-gradient(circle_at_bottom_right,rgba(139,92,246,0.12),transparent_36%)]" />
                <div className="relative">
                  <div className="text-5xl font-bold tracking-[-0.05em] text-white">{metric.value}</div>
                  <div className="mt-4 text-xl font-semibold text-slate-100">{metric.label}</div>
                  <p className="mt-3 text-sm leading-6 text-slate-300">{metric.detail}</p>
                </div>
              </motion.article>
            ))}
          </motion.div>
        </SectionShell>

        <SectionShell>
          <div className="grid items-center gap-10 lg:grid-cols-[1fr_0.95fr]">
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.25 }}
              variants={fadeInUp}
              transition={{ duration: 0.7, ease: 'easeOut' }}
              className="relative overflow-hidden rounded-[36px] border border-white/10 bg-[linear-gradient(180deg,rgba(10,15,30,0.94),rgba(10,15,30,0.74))] p-8 shadow-[0_36px_110px_-60px_rgba(34,211,238,0.72)] md:p-10"
            >
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.18),transparent_32%),radial-gradient(circle_at_bottom_right,rgba(139,92,246,0.16),transparent_34%)]" />
              <div className="relative">
                <SectionHeading
                  eyebrow="AI layer"
                  title="ИИ для маркировки и операционных процессов"
                  description="AI становится рабочим слоем поверх процессов: помогает разбирать документы, ловить аномалии и ускорять работу команды без потери контроля."
                />

                <div className="mt-8 grid gap-4">
                  {aiCapabilities.map((item) => (
                    <div
                      key={item}
                      className="flex items-start gap-3 rounded-[22px] border border-white/10 bg-white/[0.04] px-4 py-4 backdrop-blur"
                    >
                      <div className="mt-0.5 flex h-9 w-9 items-center justify-center rounded-2xl border border-cyan-300/20 bg-cyan-400/10 text-cyan-200">
                        <Sparkles className="h-4 w-4" />
                      </div>
                      <p className="text-sm leading-6 text-slate-200">{item}</p>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>

            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.25 }}
              variants={fadeIn}
              transition={{ duration: 0.8, ease: 'easeOut', delay: 0.1 }}
              className="relative mx-auto h-[32rem] w-full max-w-[34rem]"
            >
              <div className="absolute inset-0 rounded-[36px] border border-white/10 bg-[linear-gradient(180deg,rgba(11,16,32,0.88),rgba(8,12,23,0.7))]" />
              <motion.div
                className="absolute left-1/2 top-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(circle,rgba(56,189,248,0.36),rgba(59,130,246,0.16)_40%,rgba(139,92,246,0.12)_62%,transparent_72%)] blur-[2px]"
                animate={{ scale: [1, 1.08, 0.96, 1] }}
                transition={{ duration: 10, repeat: Number.POSITIVE_INFINITY, ease: 'easeInOut' }}
              />
              <motion.div
                className="absolute left-1/2 top-1/2 h-80 w-80 -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-300/20"
                animate={{ rotate: 360 }}
                transition={{ duration: 30, repeat: Number.POSITIVE_INFINITY, ease: 'linear' }}
              />
              <motion.div
                className="absolute left-1/2 top-1/2 h-56 w-56 -translate-x-1/2 -translate-y-1/2 rounded-full border border-violet-300/20"
                animate={{ rotate: -360 }}
                transition={{ duration: 18, repeat: Number.POSITIVE_INFINITY, ease: 'linear' }}
              />

              {[
                { className: 'left-[20%] top-[22%]', color: 'bg-cyan-300' },
                { className: 'left-[67%] top-[28%]', color: 'bg-violet-300' },
                { className: 'left-[30%] top-[62%]', color: 'bg-blue-300' },
                { className: 'left-[62%] top-[68%]', color: 'bg-cyan-200' },
                { className: 'left-[49%] top-[44%]', color: 'bg-white' },
              ].map((node, index) => (
                <motion.div
                  key={node.className}
                  className={`absolute h-3 w-3 rounded-full ${node.color} ${node.className} shadow-[0_0_20px_currentColor]`}
                  animate={{ scale: [1, 1.5, 1], opacity: [0.7, 1, 0.7] }}
                  transition={{ duration: 3 + index, repeat: Number.POSITIVE_INFINITY, ease: 'easeInOut' }}
                />
              ))}

              <div className="absolute left-[14%] top-[18%] h-px w-[58%] rotate-[16deg] bg-gradient-to-r from-cyan-300/0 via-cyan-300/70 to-cyan-300/0" />
              <div className="absolute left-[26%] top-[58%] h-px w-[44%] -rotate-[18deg] bg-gradient-to-r from-violet-300/0 via-violet-300/70 to-violet-300/0" />
              <div className="absolute left-[30%] top-[35%] h-px w-[38%] rotate-[48deg] bg-gradient-to-r from-blue-300/0 via-blue-300/65 to-blue-300/0" />

              <motion.div
                variants={fadeInUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, amount: 0.4 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="absolute left-6 top-8 w-[17rem] rounded-[24px] border border-white/10 bg-slate-950/60 p-4 shadow-[0_18px_60px_-30px_rgba(59,130,246,0.8)] backdrop-blur-xl"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-cyan-300/20 bg-cyan-400/10 text-cyan-200">
                    <MessageSquareText className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white">AI Ассистент</div>
                    <div className="text-xs text-slate-400">подсказка оператору</div>
                  </div>
                </div>
                <p className="mt-4 text-sm leading-6 text-slate-200">
                  У партии 3 позиции с риском ошибки в кодах. Проверить агрегацию по складу №4?
                </p>
              </motion.div>

              <motion.div
                variants={fadeInUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, amount: 0.4 }}
                transition={{ duration: 0.6, delay: 0.28 }}
                className="absolute bottom-10 right-6 w-[15rem] rounded-[24px] border border-white/10 bg-slate-950/60 p-4 shadow-[0_18px_60px_-30px_rgba(139,92,246,0.8)] backdrop-blur-xl"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-violet-300/20 bg-violet-400/10 text-violet-200">
                    <Send className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white">Telegram bot</div>
                    <div className="text-xs text-slate-400">операционный сценарий</div>
                  </div>
                </div>
                <p className="mt-4 text-sm leading-6 text-slate-200">
                  Статус заказа обновлён. Документы сверены, отклонений не найдено.
                </p>
              </motion.div>
            </motion.div>
          </div>
        </SectionShell>

        <SectionShell id="cta" className="pb-24 pt-10">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.35 }}
            variants={fadeInUp}
            transition={{ duration: 0.7, ease: 'easeOut' }}
            className="relative overflow-hidden rounded-[40px] border border-white/10 bg-[linear-gradient(180deg,rgba(11,16,32,0.94),rgba(10,15,30,0.76))] px-6 py-10 shadow-[0_40px_120px_-65px_rgba(59,130,246,0.85)] md:px-10 md:py-14"
          >
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(34,211,238,0.18),transparent_24%),radial-gradient(circle_at_bottom_left,rgba(139,92,246,0.16),transparent_30%)]" />
            <div className="relative flex flex-col items-start justify-between gap-8 lg:flex-row lg:items-center">
              <div className="max-w-2xl">
                <h2 className="text-3xl font-bold tracking-tight text-white md:text-4xl">Готовы к автоматизации?</h2>
                <p className="mt-4 text-lg leading-8 text-slate-300">
                  Поможем внедрить Честный Знак, интеграции и AI-решения под ваш бизнес.
                </p>
              </div>

              <Link
                to="/register"
                className="inline-flex items-center justify-center gap-2 rounded-2xl border border-cyan-300/25 bg-[linear-gradient(135deg,rgba(34,211,238,0.28),rgba(59,130,246,0.28))] px-7 py-4 text-base font-semibold text-white shadow-[0_20px_45px_-20px_rgba(34,211,238,0.9)] transition hover:-translate-y-0.5 hover:shadow-[0_24px_60px_-18px_rgba(59,130,246,0.95)]"
              >
                Оставить заявку
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </motion.div>
        </SectionShell>
      </main>

      <footer className="relative z-10 border-t border-white/10 bg-slate-950/35">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-8 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.06] text-cyan-100">
              <PackageCheck className="h-5 w-5" />
            </div>
            <div>
              <div className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Prime Trace</div>
              <div className="text-sm text-slate-300">© 2026. Enterprise automation systems.</div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-slate-400">
            {footerLinks.map((link) => (
              <a key={link.label} href={link.href} className="transition hover:text-white">
                {link.label}
              </a>
            ))}
            <a href="https://t.me/company" className="transition hover:text-white">
              Telegram
            </a>
            <a href="mailto:hello@company.ru" className="transition hover:text-white">
              hello@company.ru
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export { HomePage };
