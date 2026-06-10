import Link from "next/link";
import {
  ArrowRight,
  Bot,
  Building2,
  Car,
  Check,
  ChevronRight,
  FileCheck2,
  Home,
  Mail,
  MapPin,
  Menu,
  Plane,
  ShieldCheck,
  Sparkles,
  WalletCards,
} from "lucide-react";

import { LanguageSwitcher } from "@/components/language-switcher";

const heroImages = [
  {
    src: "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&w=900&q=80",
    alt: "Conseiller assurance automobile avec un client",
  },
  {
    src: "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=900&q=80",
    alt: "Maison familiale assuree",
  },
  {
    src: "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=900&q=80",
    alt: "Voyageur avec passeport et valise",
  },
  {
    src: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=900&q=80",
    alt: "Tableau de bord de gestion intelligente",
  },
];

const automatedTasks = [
  "Creation automatique de clients",
  "Creation de devis",
  "Creation de polices d'assurance",
  "Analyse des documents clients",
  "Verification des pieces justificatives",
  "Calcul de primes",
  "Suivi des paiements",
  "Generation de recus",
  "Gestion des renouvellements",
  "Gestion des sinistres",
  "Generation de courriers",
  "Creation de rapports",
  "Rappels automatiques",
  "Detection des dossiers incomplets",
  "Assistance aux conseillers",
];

const insuranceTypes = [
  {
    title: "Assurance automobile",
    icon: Car,
    image:
      "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=900&q=80",
    features: [
      "Analyse du vehicule",
      "Verification du permis de conduire",
      "Creation de devis auto",
      "Calcul automatique de prime",
      "Suivi des accidents",
      "Gestion des sinistres auto",
      "Renouvellement automatique des polices",
    ],
  },
  {
    title: "Assurance habitation",
    icon: Home,
    image:
      "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=900&q=80",
    features: [
      "Enregistrement des biens assures",
      "Analyse des risques lies au logement",
      "Creation de devis habitation",
      "Gestion des garanties",
      "Suivi des sinistres habitation",
      "Generation des contrats",
      "Gestion des paiements",
    ],
  },
  {
    title: "Assurance voyage",
    icon: Plane,
    image:
      "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80",
    features: [
      "Creation de devis voyage",
      "Analyse de la destination",
      "Gestion des dates de voyage",
      "Verification des garanties medicales",
      "Generation de certificat d'assurance voyage",
      "Assistance client avant le depart",
      "Suivi des reclamations",
    ],
  },
];

const agents = [
  {
    title: "Agent IA Client",
    icon: Building2,
    tasks: [
      "Creation de profils clients",
      "Mise a jour des informations",
      "Analyse des documents",
      "Verification des informations manquantes",
    ],
  },
  {
    title: "Agent IA Devis",
    icon: Sparkles,
    tasks: [
      "Generation de devis personnalises",
      "Comparaison des offres",
      "Calcul des primes",
      "Envoi du devis au client",
    ],
  },
  {
    title: "Agent IA Police d'assurance",
    icon: ShieldCheck,
    tasks: [
      "Creation des contrats",
      "Generation des documents PDF",
      "Attribution des numeros de police",
      "Suivi des dates d'expiration",
    ],
  },
  {
    title: "Agent IA Sinistre",
    icon: FileCheck2,
    tasks: [
      "Enregistrement des sinistres",
      "Analyse des pieces justificatives",
      "Suivi du statut des dossiers",
      "Generation des rapports de sinistre",
    ],
  },
  {
    title: "Agent IA Paiement",
    icon: WalletCards,
    tasks: [
      "Suivi des paiements",
      "Generation de recus",
      "Detection des retards",
      "Relances automatiques",
    ],
  },
  {
    title: "Agent IA Document",
    icon: FileCheck2,
    tasks: [
      "Generation de contrats",
      "Generation de certificats",
      "Generation de recus",
      "Classement automatique des documents",
    ],
  },
  {
    title: "Agent IA Reporting",
    icon: Bot,
    tasks: [
      "Statistiques clients",
      "Statistiques de ventes",
      "Rapports de sinistres",
      "Rapports financiers",
      "Tableaux de bord decisionnels",
    ],
  },
];

const pricingPlans = [
  {
    name: "Basic",
    automation: "0%",
    description: "Gestion manuelle des operations d'assurance.",
    inclusions: [
      "Gestion des clients",
      "Gestion des devis",
      "Gestion des contrats",
      "Gestion des paiements",
      "Gestion des documents",
      "Gestion manuelle des sinistres",
      "Aucun Agent IA inclus",
    ],
  },
  {
    name: "Pro",
    automation: "40%",
    description: "Automatisation partielle avec Agent IA a 40%.",
    featured: true,
    inclusions: [
      "Toutes les fonctionnalites du Plan Basic",
      "Agent IA Client",
      "Agent IA Devis",
      "Agent IA Documents",
      "Automatisation jusqu'a 40%",
      "Assistance intelligente limitee",
    ],
  },
  {
    name: "Max",
    automation: "70%",
    description: "Automatisation avancee avec Agent IA a 70%.",
    inclusions: [
      "Toutes les fonctionnalites du Plan Pro",
      "Agent IA Sinistre",
      "Agent IA Paiement",
      "Agent IA Reporting",
      "Automatisation jusqu'a 70%",
      "Alertes et relances automatiques",
      "Analyse intelligente des dossiers",
    ],
  },
  {
    name: "Max Plus",
    automation: "100%",
    description: "Capacite complete de l'Agent IA pour une automatisation maximale.",
    inclusions: [
      "Toutes les fonctionnalites du Plan Max",
      "Tous les Agents IA",
      "Automatisation complete",
      "Analyse avancee",
      "Generation automatique de documents",
      "Workflows intelligents",
      "Rapports decisionnels",
      "Assistance IA prioritaire",
    ],
  },
];

const gallery = [
  {
    src: "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=900&q=80",
    label: "Signature d'une assurance automobile",
  },
  {
    src: "https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=900&q=80",
    label: "Famille devant une maison assuree",
  },
  {
    src: "https://images.unsplash.com/photo-1517400508447-f8dd518b86db?auto=format&fit=crop&w=900&q=80",
    label: "Voyageur avec passeport et valise",
  },
  {
    src: "https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&w=900&q=80",
    label: "Conseiller utilisant un tableau de bord IA",
  },
  {
    src: "https://images.unsplash.com/photo-1554224155-6726b3ff858f?auto=format&fit=crop&w=900&q=80",
    label: "Agent IA analysant des documents",
  },
  {
    src: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=900&q=80",
    label: "Dashboard moderne de gestion d'assurance",
  },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[#f7f9fb] text-[#162033]">
      <header className="fixed inset-x-0 top-0 z-50 border-b border-white/70 bg-white/90 backdrop-blur-xl">
        <nav className="mx-auto flex h-20 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link href="#accueil" className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-lg bg-[#07111f] text-white">
              <ShieldCheck className="h-6 w-6" aria-hidden="true" />
            </span>
            <span className="text-xl font-semibold tracking-tight text-[#07111f]">
              TinsurAI
            </span>
          </Link>

          <div className="hidden items-center gap-8 lg:flex">
            {["Accueil", "Fonctionnalites", "Tarification", "Contact"].map(
              (item) => (
                <Link
                  key={item}
                  href={`#${item.toLowerCase()}`}
                  className="text-sm font-medium text-slate-600 transition hover:text-[#07111f]"
                >
                  {item}
                </Link>
              ),
            )}
          </div>

          <div className="flex items-center gap-2">
            <LanguageSwitcher />
            <Link
              href="/register"
              className="inline-flex rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 sm:px-4 sm:text-sm"
            >
              S'enregistrer
            </Link>
            <Link
              href="/login"
              className="rounded-lg bg-[#07111f] px-3 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-[#123154] sm:px-4 sm:text-sm"
            >
              Se connecter
            </Link>
            <details className="relative lg:hidden">
              <summary className="inline-flex h-10 w-10 cursor-pointer list-none items-center justify-center rounded-lg border border-slate-200 text-slate-700 marker:hidden">
                <Menu className="h-5 w-5" aria-hidden="true" />
                <span className="sr-only">Ouvrir le menu</span>
              </summary>
              <div className="absolute right-0 mt-3 grid w-56 gap-1 rounded-lg border border-slate-200 bg-white p-2 shadow-xl">
                {["Accueil", "Fonctionnalites", "Tarification", "Contact"].map(
                  (item) => (
                    <Link
                      key={item}
                      href={`#${item.toLowerCase()}`}
                      className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
                    >
                      {item}
                    </Link>
                  ),
                )}
              </div>
            </details>
          </div>
        </nav>
      </header>

      <section
        id="accueil"
        className="relative overflow-hidden bg-white pt-28 sm:pt-32"
      >
        <div className="mx-auto grid max-w-7xl gap-12 px-4 pb-16 sm:px-6 lg:grid-cols-[1fr_0.95fr] lg:px-8 lg:pb-24">
          <div className="flex flex-col justify-center">
            <div className="mb-6 inline-flex w-fit items-center gap-2 rounded-full border border-[#b7d7ce] bg-[#eefaf6] px-4 py-2 text-sm font-semibold text-[#0c6b57]">
              <Bot className="h-4 w-4" aria-hidden="true" />
              Plateforme IA pour compagnies, courtiers et agences
            </div>
            <h1 className="max-w-4xl text-4xl font-semibold leading-tight tracking-normal text-[#07111f] sm:text-5xl lg:text-6xl">
              TinsurAI - L'intelligence artificielle au service de la gestion
              d'assurance
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              Automatisez vos taches d'assurance, gerez vos clients, vos
              contrats, vos sinistres, vos paiements et vos documents avec des
              Agents IA specialises.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link
                href="/register"
                className="inline-flex items-center justify-center rounded-lg bg-[#07111f] px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/15 transition hover:bg-[#123154]"
              >
                Commencer maintenant
                <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
              </Link>
              <Link
                href="#fonctionnalites"
                className="inline-flex items-center justify-center rounded-lg border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-800 transition hover:border-slate-400 hover:bg-slate-50"
              >
                Decouvrir les fonctionnalites
              </Link>
            </div>
            <div className="mt-10 grid max-w-2xl grid-cols-3 gap-4 border-t border-slate-200 pt-8">
              {[
                ["15+", "taches automatisees"],
                ["3", "lignes d'assurance"],
                ["100%", "workflows evolutifs"],
              ].map(([value, label]) => (
                <div key={label}>
                  <p className="text-2xl font-semibold text-[#07111f]">
                    {value}
                  </p>
                  <p className="mt-1 text-sm text-slate-500">{label}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="relative min-h-[520px]">
            <div className="absolute inset-0 rounded-[2rem] bg-[#dff3ec]" />
            <div className="relative grid h-full grid-cols-2 gap-4 p-4">
              {heroImages.map((image, index) => (
                <img
                  key={image.src}
                  src={image.src}
                  alt={image.alt}
                  className={`h-full min-h-56 w-full rounded-2xl object-cover shadow-xl shadow-slate-900/10 ${
                    index === 1 ? "translate-y-8" : ""
                  } ${index === 2 ? "-translate-y-8" : ""}`}
                />
              ))}
            </div>
            <div className="absolute bottom-8 left-8 right-8 rounded-2xl border border-white/80 bg-white/90 p-5 shadow-2xl shadow-slate-900/15 backdrop-blur">
              <div className="flex items-start gap-4">
                <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-[#07111f] text-white">
                  <Sparkles className="h-6 w-6" aria-hidden="true" />
                </span>
                <div>
                  <p className="font-semibold text-[#07111f]">
                    Agent IA assistant un conseiller assurance
                  </p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">
                    Analyse les pieces, detecte les donnees manquantes et
                    prepare les prochaines actions.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-y border-slate-200 bg-[#07111f] py-10 text-white">
        <div className="mx-auto grid max-w-7xl gap-6 px-4 sm:px-6 lg:grid-cols-[0.8fr_1.2fr] lg:px-8">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#8ee3cf]">
              Productivite augmentee
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-normal">
              Des Agents IA pour accelerer les operations d'assurance.
            </h2>
          </div>
          <p className="text-base leading-8 text-slate-300">
            TinsurAI automatise les taches repetitives et aide les equipes a
            traiter plus vite les dossiers clients, devis, contrats, sinistres,
            paiements, documents et rapports, tout en gardant une experience
            claire pour les conseillers.
          </p>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {automatedTasks.map((task) => (
            <div
              key={task}
              className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-md"
            >
              <Check className="mb-4 h-5 w-5 text-[#0c8f72]" aria-hidden="true" />
              <p className="text-sm font-medium leading-6 text-slate-700">
                {task}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-white py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#0c8f72]">
              Types d'assurances
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-normal text-[#07111f] sm:text-4xl">
              Automobile, habitation et voyage dans un meme espace intelligent.
            </h2>
          </div>
          <div className="mt-10 grid gap-6 lg:grid-cols-3">
            {insuranceTypes.map((type) => {
              const Icon = type.icon;
              return (
                <article
                  key={type.title}
                  className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm"
                >
                  <img
                    src={type.image}
                    alt={type.title}
                    className="h-56 w-full object-cover"
                  />
                  <div className="p-6">
                    <div className="flex items-center gap-3">
                      <span className="flex h-11 w-11 items-center justify-center rounded-lg bg-[#eefaf6] text-[#0c8f72]">
                        <Icon className="h-5 w-5" aria-hidden="true" />
                      </span>
                      <h3 className="text-xl font-semibold text-[#07111f]">
                        {type.title}
                      </h3>
                    </div>
                    <ul className="mt-5 space-y-3">
                      {type.features.map((feature) => (
                        <li
                          key={feature}
                          className="flex gap-3 text-sm leading-6 text-slate-600"
                        >
                          <ChevronRight
                            className="mt-1 h-4 w-4 shrink-0 text-[#0c8f72]"
                            aria-hidden="true"
                          />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section id="fonctionnalites" className="py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
            <div className="max-w-3xl">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#0c8f72]">
                Fonctionnalites
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-normal text-[#07111f] sm:text-4xl">
                Chaque Agent IA prend en charge un flux metier precis.
              </h2>
            </div>
            <Link
              href="#tarification"
              className="inline-flex w-fit items-center rounded-lg border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-800 transition hover:border-slate-400"
            >
              Voir les plans
              <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
          <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {agents.map((agent) => {
              const Icon = agent.icon;
              return (
                <article
                  key={agent.title}
                  className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-md"
                >
                  <span className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#07111f] text-white">
                    <Icon className="h-6 w-6" aria-hidden="true" />
                  </span>
                  <h3 className="mt-5 text-xl font-semibold text-[#07111f]">
                    {agent.title}
                  </h3>
                  <p className="mt-2 text-sm font-medium text-slate-500">
                    Automatise :
                  </p>
                  <ul className="mt-4 space-y-3">
                    {agent.tasks.map((task) => (
                      <li
                        key={task}
                        className="flex gap-3 text-sm leading-6 text-slate-600"
                      >
                        <Check
                          className="mt-1 h-4 w-4 shrink-0 text-[#0c8f72]"
                          aria-hidden="true"
                        />
                        {task}
                      </li>
                    ))}
                  </ul>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section id="tarification" className="bg-white py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#0c8f72]">
              Tarification
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-normal text-[#07111f] sm:text-4xl">
              Quatre plans pour avancer au bon niveau d'automatisation.
            </h2>
          </div>
          <div className="mt-10 grid gap-6 lg:grid-cols-4">
            {pricingPlans.map((plan) => (
              <article
                key={plan.name}
                className={`rounded-lg border p-6 shadow-sm ${
                  plan.featured
                    ? "border-[#0c8f72] bg-[#eefaf6]"
                    : "border-slate-200 bg-white"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-2xl font-semibold text-[#07111f]">
                      {plan.name}
                    </h3>
                    <p className="mt-2 text-sm leading-6 text-slate-600">
                      {plan.description}
                    </p>
                  </div>
                  <span className="rounded-lg bg-[#07111f] px-3 py-2 text-sm font-semibold text-white">
                    {plan.automation}
                  </span>
                </div>
                <ul className="mt-6 space-y-3">
                  {plan.inclusions.map((item) => (
                    <li
                      key={item}
                      className="flex gap-3 text-sm leading-6 text-slate-700"
                    >
                      <Check
                        className="mt-1 h-4 w-4 shrink-0 text-[#0c8f72]"
                        aria-hidden="true"
                      />
                      {item}
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#0c8f72]">
              Images realistes
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-normal text-[#07111f] sm:text-4xl">
              Une identite visuelle professionnelle pour chaque parcours
              assurance.
            </h2>
          </div>
          <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {gallery.map((image) => (
              <figure
                key={image.label}
                className="group overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm"
              >
                <img
                  src={image.src}
                  alt={image.label}
                  className="h-64 w-full object-cover transition duration-500 group-hover:scale-105"
                />
                <figcaption className="p-4 text-sm font-semibold text-slate-700">
                  {image.label}
                </figcaption>
              </figure>
            ))}
          </div>
        </div>
      </section>

      <section id="contact" className="bg-[#07111f] py-20 text-white">
        <div className="mx-auto grid max-w-7xl gap-10 px-4 sm:px-6 lg:grid-cols-[0.85fr_1.15fr] lg:px-8">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#8ee3cf]">
              Contact
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-normal sm:text-4xl">
              Parlons de votre prochaine plateforme d'assurance intelligente.
            </h2>
            <p className="mt-5 text-base leading-8 text-slate-300">
              TinsurAI accompagne les compagnies, courtiers et agences qui
              veulent digitaliser leurs operations avec des Agents IA utiles,
              controlables et orientes productivite.
            </p>
            <div className="mt-8 space-y-4 text-sm text-slate-300">
              <p className="flex gap-3">
                <MapPin className="h-5 w-5 text-[#8ee3cf]" aria-hidden="true" />
                Abidjan, Cote d'Ivoire
              </p>
              <p className="flex gap-3">
                <Mail className="h-5 w-5 text-[#8ee3cf]" aria-hidden="true" />
                contact@tinsurai.com
              </p>
              <p className="flex gap-3">
                <WalletCards
                  className="h-5 w-5 text-[#8ee3cf]"
                  aria-hidden="true"
                />
                +225 07 00 00 00 00
              </p>
            </div>
            <div className="mt-8 flex gap-3">
              {["LinkedIn", "X", "Facebook"].map((social) => (
                <a
                  key={social}
                  href="#contact"
                  className="rounded-lg border border-white/20 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10"
                >
                  {social}
                </a>
              ))}
            </div>
          </div>

          <form className="rounded-lg border border-white/10 bg-white p-6 text-[#07111f] shadow-2xl shadow-black/20">
            <div className="grid gap-4 sm:grid-cols-2">
              {[
                ["Nom", "text"],
                ["Email", "email"],
                ["Telephone", "tel"],
                ["Sujet", "text"],
              ].map(([label, type]) => (
                <label key={label} className="text-sm font-semibold">
                  {label}
                  <input
                    type={type}
                    className="mt-2 h-12 w-full rounded-lg border border-slate-200 px-4 text-sm outline-none transition focus:border-[#0c8f72] focus:ring-4 focus:ring-[#0c8f72]/10"
                    placeholder={label}
                  />
                </label>
              ))}
            </div>
            <label className="mt-4 block text-sm font-semibold">
              Message
              <textarea
                rows={5}
                className="mt-2 w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-[#0c8f72] focus:ring-4 focus:ring-[#0c8f72]/10"
                placeholder="Decrivez votre besoin"
              />
            </label>
            <button
              type="button"
              className="mt-5 inline-flex w-full items-center justify-center rounded-lg bg-[#07111f] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[#123154]"
            >
              Envoyer
              <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}
