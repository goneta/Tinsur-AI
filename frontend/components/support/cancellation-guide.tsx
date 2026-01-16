import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export const CancellationGuide = () => {
    return (
        <div className="max-w-4xl mx-auto space-y-8 font-sans">
            <div className="text-center space-y-4 py-8 bg-gradient-to-r from-blue-600 to-blue-500 rounded-xl text-white shadow-lg">
                <h1 className="text-4xl font-bold">Guide de Résiliation de Police d'Assurance</h1>
                <p className="text-xl opacity-90">Processus complet et normes industrielles</p>
                <div className="flex justify-center gap-2 mt-4">
                    <Badge variant="secondary" className="bg-white/20 hover:bg-white/30 text-white border-0">Officiel</Badge>
                    <Badge variant="secondary" className="bg-white/20 hover:bg-white/30 text-white border-0">Mis à jour 2025</Badge>
                </div>
            </div>

            <section className="space-y-4">
                <h2 className="text-2xl font-bold text-blue-800 border-b-2 border-blue-100 pb-2">1. Résiliation de Police – Vue d'Ensemble</h2>
                <Card>
                    <CardContent className="pt-6">
                        <p className="mb-4">
                            La résiliation de police est la fin anticipée d'une police d'assurance avant sa date d'expiration naturelle. Elle peut être initiée par :
                        </p>
                        <ul className="list-disc pl-6 space-y-2 mb-4">
                            <li><strong>Le client</strong> (titulaire de la police)</li>
                            <li><strong>La compagnie d'assurance</strong> (assureur)</li>
                        </ul>
                        <p className="text-slate-600">
                            Chaque cas présente des conditions légales, des périodes de préavis et des conséquences financières différentes.
                        </p>
                    </CardContent>
                </Card>
            </section>

            <section className="space-y-4">
                <h2 className="text-2xl font-bold text-blue-800 border-b-2 border-blue-100 pb-2">2. Résiliation Initiée par le Client</h2>

                <div className="grid md:grid-cols-2 gap-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Raisons Courantes</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="list-disc pl-6 space-y-2 text-slate-700">
                                <li>Police n'est plus nécessaire (véhicule vendu, changement de mode de vie)</li>
                                <li>Couverture moins chère ou meilleure trouvée</li>
                                <li>Insatisfaction du service</li>
                                <li>Couverture en double</li>
                            </ul>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Conditions pour la Résiliation Client</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="list-disc pl-6 space-y-2 text-slate-700">
                                <li>Le client doit être le titulaire de la police</li>
                                <li>La résiliation peut généralement avoir lieu à tout moment</li>
                                <li>L'éligibilité au remboursement dépend de :
                                    <ul className="list-circle pl-6 mt-1 text-slate-600">
                                        <li>Le temps écoulé depuis le début de la police</li>
                                        <li>Si une réclamation a été faite</li>
                                        <li>Les règles de la période de rétractation</li>
                                    </ul>
                                </li>
                                <li>Des frais administratifs peuvent s'appliquer</li>
                            </ul>
                        </CardContent>
                    </Card>
                </div>

                <div className="bg-blue-50 border-l-4 border-blue-600 p-6 rounded-r-lg">
                    <h3 className="text-lg font-bold text-blue-900 mb-2">Période de Rétractation (Cooling-Off Period)</h3>
                    <p className="font-semibold mb-2">Généralement 14 jours, varie selon le pays</p>
                    <p className="mb-2">Si le client résilie pendant la période de rétractation :</p>
                    <ul className="list-disc pl-6 space-y-1 text-blue-800">
                        <li>La police est annulée avec une pénalité minimale ou nulle</li>
                        <li>Remboursement complet ou remboursement moins frais admin</li>
                        <li>La couverture est considérée comme annulée ou couverte à court terme</li>
                    </ul>
                </div>

                <div className="space-y-4 mt-6">
                    <h3 className="text-xl font-bold text-blue-700">Processus de Résiliation Client (Flux Système)</h3>
                    <div className="space-y-2">
                        {[
                            "Le client sélectionne 'Annuler la Police' depuis la carte de police",
                            "Le système affiche : Options de raison et Estimation du remboursement",
                            "Le client confirme la résiliation",
                            "Le statut de la police passe à Annulée (Initiée par le Client)",
                            "Le système : Arrête la couverture, Calcule le remboursement, Génère les documents",
                            "Confirmation de résiliation envoyée au client"
                        ].map((step, i) => (
                            <div key={i} className="flex items-start gap-3 bg-slate-50 p-3 rounded border border-slate-100">
                                <span className="bg-blue-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold shrink-0">
                                    {i + 1}
                                </span>
                                <span className="text-slate-700">{step}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="space-y-4 mt-6">
                    <h3 className="text-xl font-bold text-blue-700">Règles de Remboursement (Typiques)</h3>
                    <div className="overflow-hidden rounded-lg border border-slate-200">
                        <table className="w-full text-sm">
                            <thead className="bg-slate-100 text-slate-700">
                                <tr>
                                    <th className="p-3 text-left font-bold">Scénario</th>
                                    <th className="p-3 text-left font-bold">Remboursement</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                <tr><td className="p-3">Dans la période de rétractation, sans réclamation</td><td className="p-3">Remboursement complet ou quasi-complet</td></tr>
                                <tr><td className="p-3">Après la période de rétractation, sans réclamation</td><td className="p-3">Remboursement pro-rata</td></tr>
                                <tr><td className="p-3">Réclamation déjà faite</td><td className="p-3">Aucun remboursement</td></tr>
                                <tr><td className="p-3">Plan de paiement mensuel</td><td className="p-3">Les paiements s'arrêtent, pas de remboursement</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            <section className="space-y-4">
                <h2 className="text-2xl font-bold text-blue-800 border-b-2 border-blue-100 pb-2">3. Résiliation Initiée par la Compagnie d'Assurance</h2>

                <div className="grid md:grid-cols-2 gap-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Raisons Courantes</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="list-disc pl-6 space-y-2 text-slate-700">
                                <li>Non-paiement des primes</li>
                                <li>Fausse déclaration ou fraude</li>
                                <li>Violation des conditions de la police</li>
                                <li>Risque élevé découvert après souscription</li>
                                <li>Exigence réglementaire ou légale</li>
                            </ul>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Conditions pour la Résiliation par l'Assureur</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="list-disc pl-6 space-y-2 text-slate-700">
                                <li>Doit respecter les périodes de préavis légales</li>
                                <li>Doit fournir une raison claire</li>
                                <li>Ne peut pas résilier arbitrairement</li>
                                <li>Certaines raisons permettent une résiliation immédiate (fraude)</li>
                            </ul>
                        </CardContent>
                    </Card>
                </div>

                <div className="space-y-4 mt-6">
                    <h3 className="text-xl font-bold text-blue-700">Périodes de Préavis (Typiques)</h3>
                    <div className="overflow-hidden rounded-lg border border-slate-200">
                        <table className="w-full text-sm">
                            <thead className="bg-slate-100 text-slate-700">
                                <tr>
                                    <th className="p-3 text-left font-bold">Raison</th>
                                    <th className="p-3 text-left font-bold">Préavis Typique</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                <tr><td className="p-3">Non-paiement</td><td className="p-3">7–14 jours</td></tr>
                                <tr><td className="p-3">Fausse déclaration</td><td className="p-3">Immédiat</td></tr>
                                <tr><td className="p-3">Risque accru</td><td className="p-3">14–30 jours</td></tr>
                                <tr><td className="p-3">Erreur administrative</td><td className="p-3">Immédiat ou correctif</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div className="space-y-4 mt-6">
                    <h3 className="text-xl font-bold text-blue-700">Processus de Résiliation par l'Assureur (Flux Système)</h3>
                    <div className="space-y-2">
                        {[
                            "Admin/Employé initie la résiliation",
                            "Raison de résiliation sélectionnée (obligatoire)",
                            "Le système valide : Période de préavis et Éligibilité au remboursement",
                            "Le statut de la police passe à Résiliation en Attente",
                            "Le client est notifié (email + portail)",
                            "La couverture se termine à la date effective",
                            "Le statut de la police devient Annulée (Initiée par l'Assureur)",
                            "Documents de résiliation générés et stockés"
                        ].map((step, i) => (
                            <div key={i} className="flex items-start gap-3 bg-slate-50 p-3 rounded border border-slate-100">
                                <span className="bg-blue-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold shrink-0">
                                    {i + 1}
                                </span>
                                <span className="text-slate-700">{step}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <section className="space-y-4">
                <h2 className="text-2xl font-bold text-blue-800 border-b-2 border-blue-100 pb-2">4. Différences Clés : Résiliation Client vs Assureur</h2>
                <div className="overflow-x-auto rounded-lg border border-slate-200 shadow-sm">
                    <table className="w-full text-sm">
                        <thead className="bg-blue-600 text-white">
                            <tr>
                                <th className="p-3 text-left font-bold">Aspect</th>
                                <th className="p-3 text-left font-bold">Client Résilie</th>
                                <th className="p-3 text-left font-bold">Assureur Résilie</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 bg-white">
                            <tr>
                                <td className="p-3 font-medium text-slate-700">Qui initie</td>
                                <td className="p-3 text-slate-600">Client</td>
                                <td className="p-3 text-slate-600">Compagnie d'assurance</td>
                            </tr>
                            <tr className="bg-slate-50">
                                <td className="p-3 font-medium text-slate-700">Préavis requis</td>
                                <td className="p-3 text-slate-600">Généralement aucun</td>
                                <td className="p-3 text-slate-600">Obligatoire</td>
                            </tr>
                            <tr>
                                <td className="p-3 font-medium text-slate-700">Remboursement possible</td>
                                <td className="p-3 text-slate-600">Oui (conditions s'appliquent)</td>
                                <td className="p-3 text-slate-600">Oui (sauf fraude)</td>
                            </tr>
                            <tr className="bg-slate-50">
                                <td className="p-3 font-medium text-slate-700">Raison requise</td>
                                <td className="p-3 text-slate-600">Optionnelle</td>
                                <td className="p-3 text-slate-600">Obligatoire</td>
                            </tr>
                            <tr>
                                <td className="p-3 font-medium text-slate-700">Sensibilité légale</td>
                                <td className="p-3 text-slate-600">Moyenne</td>
                                <td className="p-3 text-slate-600">Élevée</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <section className="space-y-4">
                <h2 className="text-2xl font-bold text-blue-800 border-b-2 border-blue-100 pb-2">5. Informations Supplémentaires</h2>

                <div className="grid md:grid-cols-2 gap-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Statuts de Police Liés</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="space-y-2">
                                <li className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-green-500"></div><span className="font-semibold text-slate-700">Active</span> - Police en cours</li>
                                <li className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-yellow-400"></div><span className="font-semibold text-slate-700">Résiliation en Attente</span> - Processus initié</li>
                                <li className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-red-500"></div><span className="font-semibold text-slate-700">Annulée (Client)</span> - Par le titulaire</li>
                                <li className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-red-700"></div><span className="font-semibold text-slate-700">Annulée (Assureur)</span> - Par la compagnie</li>
                                <li className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-slate-400"></div><span className="font-semibold text-slate-700">Suspendue</span> - Temporaire, non annulée</li>
                            </ul>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Documents Générés</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="list-disc pl-6 space-y-2 text-slate-700">
                                <li>Confirmation de résiliation</li>
                                <li>Relevé de calcul de remboursement (le cas échéant)</li>
                                <li>Programme de police mis à jour</li>
                                <li>Preuve de date de fin de couverture</li>
                            </ul>
                            <p className="mt-4 text-sm text-slate-500 italic">
                                Note : Tous les documents doivent apparaître dans Voir Documents → Votre Compte
                            </p>
                        </CardContent>
                    </Card>
                </div>
            </section>

            <section className="space-y-6">
                <h2 className="text-2xl font-bold text-blue-800 border-b-2 border-blue-100 pb-2">7. Meilleures Pratiques pour Votre Plateforme</h2>

                <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg">
                        <h3 className="text-lg font-bold text-green-800 mb-2">UX (Expérience Utilisateur)</h3>
                        <p className="font-bold text-green-900 mb-2">Toujours afficher :</p>
                        <ul className="list-disc pl-6 space-y-1 text-green-800">
                            <li>Date de résiliation effective</li>
                            <li>Montant du remboursement (le cas échéant)</li>
                            <li>Exiger une confirmation avant la résiliation finale</li>
                        </ul>
                    </div>

                    <div className="bg-yellow-50 border-l-4 border-yellow-500 p-6 rounded-r-lg">
                        <h3 className="text-lg font-bold text-yellow-800 mb-2">Conformité & Règles Système</h3>
                        <ul className="list-disc pl-6 space-y-1 text-yellow-800">
                            <li>Enregistrer : Qui a résilié, Quand, Pourquoi</li>
                            <li>Stocker les documents de façon permanente</li>
                            <li>Empêcher les réclamations après la date de résiliation</li>
                            <li>Verrouiller les polices annulées (lecture seule)</li>
                            <li>Ne pas permettre la réactivation</li>
                        </ul>
                    </div>
                </div>

                <div className="flex justify-center py-8">
                    <div className="bg-slate-900 text-white px-8 py-6 rounded-xl shadow-xl max-w-2xl w-full text-center">
                        <h3 className="text-xl font-bold border-b border-slate-700 pb-4 mb-4">Diagramme d'État de Résiliation (Simplifié)</h3>
                        <div className="flex flex-col md:flex-row items-center justify-center gap-4 text-sm md:text-base">
                            <span className="font-bold text-green-400 bg-green-400/10 px-3 py-1 rounded">ACTIVE</span>
                            <span className="text-slate-500 rotating-arrow">↓</span>
                            <span className="font-bold text-yellow-400 bg-yellow-400/10 px-3 py-1 rounded">RÉSILIATION EN ATTENTE</span>
                            <span className="text-slate-500 rotating-arrow">↓</span>
                            <span className="font-bold text-red-400 bg-red-400/10 px-3 py-1 rounded text-center">
                                ANNULÉE<br />
                                <span className="text-xs font-normal opacity-75">(Client / Assureur)</span>
                            </span>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

