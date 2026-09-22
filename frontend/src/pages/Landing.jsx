import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import './Landing.css'

/** Иконки для карточек */
const ICONS = {
  suitcase: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <rect x="3" y="7" width="18" height="13" rx="2" />
      <path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
      <line x1="3" y1="12" x2="21" y2="12" />
    </svg>
  ),
  bell: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M6 10a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z" />
      <path d="M10 20a2 2 0 0 0 4 0" />
    </svg>
  ),
  document: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M8 4h6l4 4v12a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1Z" />
      <path d="M13 4v4h4" />
    </svg>
  ),
  chart: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <line x1="5" y1="20" x2="5" y2="12" />
      <line x1="12" y1="20" x2="12" y2="6" />
      <line x1="19" y1="20" x2="19" y2="15" />
    </svg>
  ),
}

const FEATURES = [
  {
    icon: 'suitcase',
    title: 'Всё в одном месте',
    text: 'Билеты, жильё, экскурсии и трансферы одной поездки собраны на одной странице.',
  },
  {
    icon: 'bell',
    title: 'Напоминания',
    text: 'Сервис заранее напоминает о датах поездки и близких перемещениях.',
  },
  {
    icon: 'document',
    title: 'Загрузка документов',
    text: 'Билеты и подтверждения бронирований можно прикрепить в формате PDF или фото.',
  },
  {
    icon: 'chart',
    title: 'Статистика поездок',
    text: 'Сколько стран и городов вы уже посетили — видно в профиле в любой момент.',
  },
]

const STEPS = [
  {
    number: '1',
    title: 'Создайте поездку',
    text: 'Укажите страну, город и даты — TripHelper заведёт для неё отдельную карточку.',
  },
  {
    number: '2',
    title: 'Добавьте детали',
    text: 'Перелёты, жильё и экскурсии — с билетами и бронями в PDF или фото.',
  },
  {
    number: '3',
    title: 'Путешествуйте спокойно',
    text: 'Сервис напомнит о датах и покажет всю поездку на одной временной линии.',
  },
]

/** Главная страница */
function Landing() {
  const { user } = useAuth()

  return (
    <div className="page-wrapper">
      <section className="hero container">
        <div
          className="hero-photo"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1600&q=70')",
          }}
        >
          <div className="hero-photo-content">
            <span className="hero-kicker">Планирование поездок без хаоса</span>
            <h1>
              Путешествия без хаоса
            </h1>
            <p className="hero-subtitle">
              TripHelper собирает билеты, жильё и планы одной поездки в одном месте и напоминает
              о важных датах, чтобы ничего не потерялось.
            </p>
            <div className="hero-actions">
              {user ? (
                <>
                  <Link to="/dashboard" className="btn btn-primary">Мои поездки</Link>
                  <Link to="/profile" className="btn btn-secondary btn-on-photo">Профиль</Link>
                </>
              ) : (
                <>
                  <Link to="/register" className="btn btn-primary">Начать бесплатно</Link>
                  <Link to="/login" className="btn btn-secondary btn-on-photo">У меня есть аккаунт</Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="steps container">
        <h2 className="section-title">Как это работает</h2>
        <div className="steps-grid">
          {STEPS.map((step) => (
            <div className="step-card" key={step.number}>
              <div className="step-number">{step.number}</div>
              <h3>{step.title}</h3>
              <p>{step.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="features container">
        {FEATURES.map((feature) => (
          <div className="feature-card" key={feature.title}>
            <div className="feature-icon">{ICONS[feature.icon]}</div>
            <h3>{feature.title}</h3>
            <p>{feature.text}</p>
          </div>
        ))}
      </section>

      <section className="cta-banner container">
        <div className="cta-banner-inner">
          {user ? (
            <>
              <h2>Продолжим планировать поездки?</h2>
              <p>Все ваши поездки, билеты и напоминания — в одном месте.</p>
              <Link to="/dashboard" className="btn btn-primary">Перейти к моим поездкам</Link>
            </>
          ) : (
            <>
              <h2>Готовы упростить свои поездки?</h2>
              <p>Регистрация занимает меньше минуты, а первую поездку можно завести сразу же.</p>
              <Link to="/register" className="btn btn-primary">Создать бесплатный аккаунт</Link>
            </>
          )}
        </div>
      </section>

      <footer className="landing-footer container">
        <span>© 2026 TripHelper</span>
        <span>Сервис-помощник путешественникам</span>
      </footer>
    </div>
  )
}

export default Landing
