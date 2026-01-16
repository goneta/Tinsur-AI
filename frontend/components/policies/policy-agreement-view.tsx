"use client";

import React, { useRef, useState } from 'react';
import { Button } from "@/components/ui/button";
import { Policy } from "@/types/policy";
import { Client } from '@/types/client';
import { formatCurrency } from "@/lib/utils";
import { Printer, Download, Loader2, ArrowLeft } from "lucide-react";
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import { QRCodeSVG } from 'qrcode.react';
import { TinsurLogo } from "@/components/ui/tinsur-logo";

interface PolicyAgreementViewProps {
    policy: Policy;
    client: Client;
    onBack: () => void;
    companyName?: string;
    companyAddress?: string;
    companyPhone?: string;
}

export function PolicyAgreementView({
    policy,
    client,
    onBack,
    companyName = "Tinsur Insurance",
    companyAddress = "Nairobi, Kenya",
    companyPhone = "+254 700 000 000"
}: PolicyAgreementViewProps) {
    const contentRef = useRef<HTMLDivElement>(null);
    const [isDownloading, setIsDownloading] = useState(false);

    // Dynamic Data Calculations
    const premiumAmount = policy.premium_amount;

    // Calculate monthly payment based on frequency
    // If frequency is monthly, use the premium amount (assuming stored as monthly if frequency is monthly)
    // If annual, divide by 11 as per the template implication ("11 monthly repayments")
    let monthlyPayment = 0;
    if (policy.premium_frequency === 'monthly') {
        monthlyPayment = premiumAmount;
    } else {
        // Assuming annual premium 
        monthlyPayment = premiumAmount / 11;
    }

    // "Prime finale": Total amount of the quote. 
    // The template says: "Coût du crédit... 9,9%".
    const interestRate = 0.099;
    const creditAmount = premiumAmount; // <premium policy amount>
    const interestAmount = creditAmount * interestRate;
    const finalPremium = creditAmount + interestAmount; // <Prime finale>

    const clientName = client.first_name && client.last_name
        ? `${client.first_name} ${client.last_name}`
        : client.business_name || policy.client_name;

    const clientAddress = client.address ? `${client.address}, ${client.city || ''}` : "Adresse non fournie";

    // QR Code Data
    const qrData = JSON.stringify({
        policy_number: policy.policy_number,
        client_name: clientName,
        amount: premiumAmount,
        company_name: companyName,
        client_id: client.id,
        company_id: policy.company_id
    });

    const handleDownloadPDF = async () => {
        setIsDownloading(true);
        const element = contentRef.current;
        if (!element) return;

        try {
            const canvas = await html2canvas(element, {
                scale: 2,
                useCORS: true,
                backgroundColor: '#ffffff',
                logging: false
            });

            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF('p', 'mm', 'a4');
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = pdf.internal.pageSize.getHeight();
            const imgWidth = canvas.width;
            const imgHeight = canvas.height;

            // Force fit to width
            const ratio = pdfWidth / imgWidth;
            const scaledHeight = imgHeight * ratio;

            let heightLeft = scaledHeight;
            let position = 0;

            pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, scaledHeight);
            heightLeft -= pdfHeight;

            while (heightLeft > 0) {
                position -= pdfHeight; // Move the image up for the next page
                pdf.addPage();
                pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, scaledHeight);
                heightLeft -= pdfHeight;
            }

            pdf.save(`Contrat_De_Pret_${policy.policy_number}.pdf`);
        } catch (error) {
            console.error("Failed to generate PDF", error);
        } finally {
            setIsDownloading(false);
        }
    };

    return (
        <div className="space-y-6 pt-6">
            <div className="flex items-center justify-between">
                <Button variant="ghost" onClick={onBack} className="flex items-center gap-2">
                    <ArrowLeft className="h-4 w-4" />
                    Back to Policy Details
                </Button>

                <div className="flex items-center gap-2 print:hidden">
                    <Button variant="outline" onClick={() => window.print()}>
                        <Printer className="mr-2 h-4 w-4" />
                        Print
                    </Button>
                    <Button onClick={handleDownloadPDF} disabled={isDownloading}>
                        {isDownloading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Download className="mr-2 h-4 w-4" />}
                        Download PDF
                    </Button>
                </div>
            </div>

            <div className="flex justify-center bg-[#f9fafb]/50 p-8 rounded-lg border border-dashed">
                <div
                    ref={contentRef}
                    className="bg-white p-[40px] text-[#333] font-sans text-[12px] leading-[1.6] border shadow-lg w-full print:shadow-none print:border-none print:p-0 print:m-0 relative"
                    style={{ maxWidth: '850px' }}
                >
                    {/* Logo */}
                    <div className="absolute top-[30px] left-[40px]">
                        <TinsurLogo size={40} />
                    </div>

                    {/* QR Code */}
                    <div className="absolute top-[30px] right-[40px] flex flex-col items-center">
                        <QRCodeSVG value={qrData} size={80} />
                        <div className="text-[9px] text-[#6b7280] mt-1">Ref: {policy.policy_number}</div>
                    </div>

                    {/* Header */}
                    <div className="mb-5 text-center pt-[50px]">
                        <h1 className="text-[18px] font-bold text-[#003da5] mb-[5px] uppercase">Contrat d'Assurance à Somme Fixe réglementé par</h1>
                        <h1 className="text-[18px] font-bold text-[#003da5] uppercase">&lt;la loi de réglementation des assurances&gt;</h1>
                        <div className="mt-[10px] text-[14px] font-bold text-[#333]">
                            Numéro de Police : {policy.policy_number}
                        </div>
                    </div>

                    {/* Section: Between who? */}
                    <h2 className="text-[14px] font-bold text-[#003da5] mt-[20px] mb-[10px]">Entre qui est conclu ce contrat ?</h2>
                    <p className="mb-[15px]">
                        Il s'agit d'un contrat entre nous, {companyName} (adresse : {companyAddress}) et vous :
                    </p>

                    <div className="bg-[#f9f9f9] p-[15px] my-[15px] border-l-4 border-[#003da5]">
                        <div className="font-bold">{clientName}</div>
                        <div>{clientAddress}</div>
                    </div>

                    <p className="mb-[15px]">
                        Ce contrat définit les termes et conditions du prêt fourni en relation avec votre police d'assurance.
                    </p>

                    {/* Table */}
                    <table className="w-full border-collapse my-[15px] text-[12px]">
                        <tbody>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] align-top font-bold w-[35%] bg-[#f9f9f9]">Description des biens financés par le contrat</td>
                                <td className="p-[10px] border border-[#ddd] align-top">Votre prêt est fourni pour financer l'achat de votre Assurance Automobile.</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] align-top font-bold bg-[#f9f9f9]">Le prix au comptant payé pour votre police (incluant la taxe sur les primes d'assurance (IPT) le cas échéant)</td>
                                <td className="p-[10px] border border-[#ddd] align-top">{formatCurrency(premiumAmount)}</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] align-top font-bold bg-[#f9f9f9]">Acompte (paiement anticipé)</td>
                                <td className="p-[10px] border border-[#ddd] align-top">{formatCurrency(0)} (A)</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] align-top font-bold bg-[#f9f9f9]">Le montant du crédit emprunté</td>
                                <td className="p-[10px] border border-[#ddd] align-top">{formatCurrency(creditAmount)} (B)</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] align-top font-bold bg-[#f9f9f9]">Coût du crédit (il s'agit des intérêts) facturé à un taux fixe simple sur le montant du crédit emprunté.</td>
                                <td className="p-[10px] border border-[#ddd] align-top">{formatCurrency(interestAmount)} (C). Il s'agit du coût total du crédit. Les intérêts sont calculés en appliquant un taux simple fixe de 9,9% à l'avance sur le montant total du crédit et en l'ajoutant immédiatement au solde dû. Le montant des intérêts ainsi calculé et appliqué sera payable dans chaque mensualité.</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] align-top font-bold bg-[#f9f9f9]">Vous acceptez de payer un total de</td>
                                <td className="p-[10px] border border-[#ddd] align-top">
                                    {formatCurrency(finalPremium)} (A+B+C)<br />
                                    Il s'agit du montant total de votre acompte, du montant que vous avez emprunté et des intérêts et autres frais. Ceci est également appelé le Montant Total à Payer.
                                </td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] align-top font-bold bg-[#f9f9f9]">Durée du contrat</td>
                                <td className="p-[10px] border border-[#ddd] align-top">11 mois</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] align-top font-bold bg-[#f9f9f9]">Nombre de paiements mensuels</td>
                                <td className="p-[10px] border border-[#ddd] align-top">11 remboursements mensuels</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] align-top font-bold bg-[#f9f9f9]">Montant des paiements mensuels</td>
                                <td className="p-[10px] border border-[#ddd] align-top">{formatCurrency(monthlyPayment)}</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] align-top font-bold bg-[#f9f9f9]">TAEG</td>
                                <td className="p-[10px] border border-[#ddd] align-top">21.1%</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] align-top font-bold bg-[#f9f9f9]">Dates de remboursement</td>
                                <td className="p-[10px] border border-[#ddd] align-top"></td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] align-top font-bold bg-[#f9f9f9]">À quoi sert le crédit ?</td>
                                <td className="p-[10px] border border-[#ddd] align-top">La prime d'assurance (incluant l'IPT le cas échéant) relative à votre police d'assurance Automobile {companyName}.</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] align-top font-bold bg-[#f9f9f9]">Comment et quand le crédit sera-t-il fourni ?</td>
                                <td className="p-[10px] border border-[#ddd] align-top">Le crédit est fourni en vous permettant de payer votre prime d'assurance annuelle par paiements différés sur une période de 11 mois. Ce crédit est fourni au moment où votre police d'assurance prend effet.</td>
                            </tr>
                        </tbody>
                    </table>

                    <p className="my-[20px]">
                        <strong>Garantie :</strong> Vous nous cédez votre police d'assurance Automobile {companyName} et vos droits en vertu de la police. Voir la section « Conditions Générales » ci-dessous pour plus de détails.
                    </p>

                    <h2 className="text-[14px] font-bold text-[#003da5] mt-[20px] mb-[10px]">Y a-t-il des frais que je pourrais devoir payer ?</h2>
                    <p className="my-[20px]">
                        Il n'y a pas d'autres frais payables en vertu de votre contrat. Nous ne facturons aucuns frais si vous êtes en retard pour effectuer un remboursement. Si vous n'effectuez pas un remboursement à temps, nous pouvons demander à votre assureur d'annuler votre couverture. Veuillez consulter vos Conditions Générales pour plus de détails.
                    </p>

                    <h2 className="text-[14px] font-bold text-[#003da5] mt-[20px] mb-[10px]">Puis-je annuler le prêt si je change d'avis au début ?</h2>
                    <p className="my-[20px]">
                        Oui - et vous n'avez pas à nous dire pourquoi vous souhaitez annuler.
                    </p>
                    <p className="my-[20px]">
                        Votre droit d'annulation commence :<br />
                        aujourd'hui si vous avez signé ce contrat en ligne et se termine après une période de 14 jours à partir de demain ; ou<br />
                        à la date à laquelle vous avez reçu votre copie de ce contrat si vous ne l'avez pas signé en ligne, et se termine après une période de 14 jours commençant le jour suivant la date à laquelle vous avez reçu votre copie de ce contrat.
                    </p>
                    <p className="my-[20px]">
                        Pour annuler votre prêt sans payer d'intérêts, vous devez :<br />
                        Nous informer que vous souhaitez annuler dans les 14 jours. Pour ce faire, appelez le {companyPhone} ou écrivez à {companyAddress}<br />
                        Rembourser le prêt dans les 30 jours suivant votre demande d'annulation. Pour ce faire, appelez le {companyPhone} pour payer par carte de débit.<br />
                        * Ce numéro peut être inclus dans les minutes d'appel inclusives fournies par votre opérateur téléphonique.
                    </p>

                    <h2 className="text-[14px] font-bold text-[#003da5] mt-[20px] mb-[10px]">Puis-je rembourser mon prêt par anticipation après les 14 jours initiaux ?</h2>
                    <p className="my-[20px]">
                        Oui. Vous avez le droit à tout moment de rembourser le crédit en cours en vertu de ce contrat en totalité ou en partie en nous contactant au {companyPhone} ou en nous écrivant à l'adresse indiquée ci-dessus.
                    </p>

                    <h2 className="text-[14px] font-bold text-[#003da5] mt-[20px] mb-[10px]">Quand mon prêt prendra-t-il fin ?</h2>
                    <p className="my-[20px]">
                        Vous pouvez rembourser votre prêt à tout moment - veuillez consulter la section « Puis-je rembourser mon prêt par anticipation après les 14 jours initiaux ? ». Sinon, votre prêt prendra fin lorsque vous aurez tout remboursé.
                    </p>

                    <h2 className="text-[14px] font-bold text-[#003da5] mt-[20px] mb-[10px]">Pouvez-vous me demander de rembourser le prêt par anticipation ?</h2>
                    <p className="my-[20px]">
                        Oui. Par exemple, cela pourrait se produire si vous êtes déclaré en faillite, si vous faites l'objet d'un Arrangement Volontaire Individuel, si vous manquez un paiement ou si vous violez gravement le contrat de prêt.
                    </p>
                    <p className="my-[20px]">
                        Si vous faites une réclamation en vertu de votre police et qu'elle est par la suite annulée ou annulée (a) la prime complète de votre police sera payable et (b) ce contrat sera résilié et toutes les sommes dues en vertu de celui-ci deviendront payables dans les 14 jours suivant l'annulation de votre police.
                    </p>
                    <p className="my-[20px]">
                        Si votre véhicule est déclaré perte totale : (a) la prime complète de votre police sera payable et (b) ce contrat sera résilié et toutes les sommes dues en vertu de celui-ci deviendront payables dans les 14 jours suivant le règlement de votre réclamation.
                    </p>

                    <h2 className="text-[14px] font-bold text-[#003da5] mt-[20px] mb-[10px]">Conditions Générales</h2>
                    <p className="my-[20px]">
                        En vertu de l'article 77B du Consumer Credit Act 1974, vous pouvez obtenir gratuitement un relevé de votre compte (Tableau d'Amortissement) à tout moment en nous demandant de vous en envoyer un. Celui-ci vous indiquera les détails de chaque versement dû en vertu de votre contrat, y compris le nombre de remboursements qu'il vous reste à effectuer, la date de chaque remboursement qu'il vous reste à effectuer et quelle partie de chaque remboursement correspond aux intérêts et au capital du prêt.
                    </p>
                    <p className="my-[20px]">
                        Si vous avez manqué un paiement, nous vous enverrons une lettre vous donnant la possibilité de vous rattraper. Nous pouvons également vous contacter pour discuter de votre situation et essayer d'organiser un paiement. Si un montant reste impayé après 14 jours, nous demanderons généralement à votre assureur d'annuler votre police. Nous enverrons tous les avis que nous devons envoyer par la loi. Si nécessaire, nous pouvons référer tout montant que vous devez à une agence tierce pour recouvrement et/ou vous poursuivre en justice pour recouvrer la dette impayée.
                    </p>
                    <p className="my-[20px]">
                        Nous pouvons transférer nos droits et obligations en vertu de notre accord avec vous à un autre prêteur ou société à l'avenir (ceci est parfois appelé une cession). Nous ne le ferons que si nous croyons raisonnablement qu'ils vous traiteront au moins de la même manière que nous.
                    </p>
                    <p className="my-[20px]">
                        Si votre adresse est en Écosse, la loi écossaise s'appliquera à votre contrat et les litiges seront renvoyés aux tribunaux écossais. Si votre adresse est en Irlande du Nord, la loi nord-irlandaise s'appliquera et votre contrat et les litiges seront renvoyés aux tribunaux nord-irlandais. Si vous vivez ailleurs, la loi anglaise s'appliquera à votre contrat et les litiges seront renvoyés aux tribunaux d'Angleterre et du Pays de Galles.
                    </p>
                    <p className="my-[20px]">
                        Nous communiquerons avec vous en anglais et vous pouvez demander une copie de ces termes et conditions à tout moment gratuitement. Notre numéro de téléphone est le {companyPhone}.
                    </p>
                    <p className="my-[20px]">
                        Pour calculer le TAEG, nous avons supposé que (i) ce contrat durera la durée indiquée ci-dessus (ii) vous et nous remplirons nos obligations en vertu de ce contrat et (iii) vous effectuerez votre premier paiement à la date la plus proche que nous autorisons.
                    </p>
                    <p className="my-[20px]">
                        À la résiliation de ce contrat, que ce soit par vous ou par nous, vous devez immédiatement rembourser le solde du Montant Total à Payer (moins toute remise applicable des frais d'intérêts), ainsi que nos frais, coûts et dépenses raisonnables engagés en vertu de ce Contrat. Pour éviter toute ambiguïté, vous restez responsable envers nous du paiement de ce montant, que nous récupérions ou non un montant auprès de l'assureur. Si nous résilions ce contrat, nous pouvons notifier l'assureur de votre manquement (le cas échéant) et, en votre nom, demander à l'assureur d'annuler la police et de nous payer les sommes mentionnées dans le point suivant.
                    </p>
                    <p className="my-[20px]">
                        Vous nous cédez, à titre de garantie, la police d'assurance Automobile {companyName} mentionnée ci-dessus et toutes les sommes qui peuvent à tout moment devenir payables en votre faveur en vertu de la police, que ce soit par remboursement de prime ou par produit de réclamations. Si vous vivez en Angleterre ou au Pays de Galles, vous donnez cette cession avec garantie de titre complet. Nous pouvons affecter ces sommes à l'acquittement de toute somme que vous nous devez en vertu de ce contrat. Lors de l'acquittement de votre dette en vertu de ce contrat, nous vous recéderons la police. Vous acceptez de conserver la police en sécurité en votre possession.
                    </p>
                    <p className="my-[20px]">
                        Vous nous autorisez à notifier l'assureur de cette cession et de toutes sommes en vertu de la police qui nous sont devenues payables en vertu du point précédent.
                    </p>
                    <p className="my-[20px]">
                        Si vous signez ce contrat en ligne, vous acceptez d'y souscrire sous forme électronique.
                    </p>
                    <p className="my-[20px]">
                        Vous pouvez avoir le droit de poursuivre l'assureur, nous ou les deux si vous recevez des services insatisfaisants en vertu de votre police d'assurance payée par crédit fourni en vertu de ce contrat.
                    </p>
                    <p className="my-[20px]">
                        {companyName} est un nom commercial de {companyName}. Notre adresse est {companyAddress}. Notre activité de crédit à la consommation est réglementée par la Financial Conduct Authority, qui peut être contactée à l'adresse suivante : 12 Endeavour Square, Londres, E20 1JN.
                    </p>
                    <p className="my-[20px]">
                        Si vous déposez une plainte, nous visons à la résoudre aussi rapidement que possible. Si vous n'êtes toujours pas satisfait, vous pouvez renvoyer votre plainte au Service de l'Ombudsman Financier (FOS). Vous pouvez en savoir plus sur le FOS en leur écrivant à Exchange Tower, Londres, E14 9SR ou en téléphonant au {companyPhone}. Des détails sont également disponibles sur leur site Web, http://www.financial-ombudsman.org.uk.
                    </p>

                    <div className="bg-[#fff3cd] border-2 border-[#ffc107] p-[15px] my-[20px] font-bold">
                        PAIEMENTS MANQUÉS - IMPORTANT !<br /><br />
                        N'oubliez pas que si vous manquez un paiement, cela pourrait avoir de graves conséquences. Cela pourrait entraîner des poursuites judiciaires de notre part contre vous, et cela pourrait affecter votre capacité à obtenir du crédit (par exemple, une carte de crédit ou un prêt hypothécaire) à l'avenir. Cela pourrait également augmenter le montant que vous payez pour le crédit.
                    </div>

                    <div className="mt-[30px] text-[11px] text-[#666] border-t-2 border-[#003da5] pt-[15px]">
                        Document généré le : <span id="date">{new Date().toLocaleDateString('fr-FR')}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
