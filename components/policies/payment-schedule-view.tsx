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

interface PaymentScheduleViewProps {
    policy: Policy;
    client: Client;
    onBack: () => void;
    companyName?: string;
    companyAddress?: string;
    companyPhone?: string;
}

export function PaymentScheduleView({
    policy,
    client,
    onBack,
    companyName = "Tinsur Insurance",
    companyAddress = "Nairobi, Kenya",
    companyPhone = "+254 700 000 000"
}: PaymentScheduleViewProps) {
    const contentRef = useRef<HTMLDivElement>(null);
    const [isDownloading, setIsDownloading] = useState(false);

    // Calculations
    const premium = policy.premium_amount;
    const insuranceLevy = 5.0; // 5%
    const monthlyPayment = policy.premium_frequency === 'annual' ? premium / 11 : premium;
    const finalPremium = premium * (1 + insuranceLevy / 100);

    const clientName = client.first_name && client.last_name
        ? `${client.first_name} ${client.last_name}`
        : client.business_name || policy.client_name;

    // QR Code Data
    const qrData = JSON.stringify({
        policy_number: policy.policy_number,
        client_name: clientName,
        amount: premium,
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

            pdf.save(`Payment_Schedule_${policy.policy_number}.pdf`);
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
                {/* Document Container - Aligned styles with PolicyAgreementView */}
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

                    <div className="text-left border-b-2 border-[#003da5] pb-4 mb-6 pt-[50px]">
                        <h1 className="text-[18px] font-bold text-[#003da5] uppercase mb-2">
                            Informations Contractuelles sur le Crédit de l'Assurance
                        </h1>
                        <div className="text-[14px] font-bold text-[#333]">
                            Numéro de Police : {policy.policy_number}
                        </div>
                    </div>

                    {/* Section 1: Coordonnées */}
                    <h2 className="text-[14px] font-bold text-[#003da5] mt-[20px] mb-[10px]">1. Coordonnées</h2>
                    <table className="w-full border-collapse mb-4 text-[12px]">
                        <tbody>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9] w-[35%]">Créancier</td>
                                <td className="p-[10px] border border-[#ddd]">{companyName}</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9]">Adresse</td>
                                <td className="p-[10px] border border-[#ddd]">{companyAddress}</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9]">Assurance Automobile</td>
                                <td className="p-[10px] border border-[#ddd]">{companyPhone}</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9]">Adresse Web</td>
                                <td className="p-[10px] border border-[#ddd]">www.tinsur.ai</td>
                            </tr>
                        </tbody>
                    </table>

                    {/* Section 2: Characteristics */}
                    <h2 className="text-[14px] font-bold text-[#003da5] mt-[20px] mb-[10px]">2. Caractéristiques principales du produit de crédit</h2>
                    <table className="w-full border-collapse mb-4 text-[12px]">
                        <tbody>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9] w-[35%]">Le type de crédit</td>
                                <td className="p-[10px] border border-[#ddd] align-top">Prêt à somme fixe</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9]">
                                    Le montant total du crédit
                                    <div className="text-[10px] text-[#6b7280] italic mt-1">Cela signifie le montant du crédit à fournir en vertu du contrat de crédit proposé ou la limite de crédit.</div>
                                </td>
                                <td className="p-[10px] border border-[#ddd] align-top">{formatCurrency(premium)}</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9]">Comment et quand le crédit serait fourni</td>
                                <td className="p-[10px] border border-[#ddd] align-top">Le crédit est fourni en vous permettant de payer votre prime d'assurance annuelle par paiements différés sur une période de 11 mois. Ce crédit est fourni au moment où votre police d'assurance prend effet.</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9]">La durée du contrat de crédit</td>
                                <td className="p-[10px] border border-[#ddd] align-top">11 mois</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9]">Remboursements</td>
                                <td className="p-[10px] border border-[#ddd] align-top">11 remboursements mensuels de {formatCurrency(monthlyPayment)}</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9]">
                                    Le montant total que vous devrez payer
                                    <div className="text-[10px] text-[#6b7280] italic mt-1">Cela signifie le montant que vous avez emprunté plus les intérêts et autres coûts.</div>
                                </td>
                                <td className="p-[10px] border border-[#ddd] align-top">{formatCurrency(finalPremium)}</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9]">Le crédit proposé sera accordé sous forme de paiement différé pour des biens ou services.</td>
                                <td className="p-[10px] border border-[#ddd] align-top">Le crédit est accordé sous forme de paiement différé pour votre police d'assurance Automobile &lt;{companyName}&gt;.</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9]">
                                    Description des biens/services/terrains (le cas échéant)
                                    <div className="text-[10px] text-[#6b7280] italic mt-1">Votre police d'assurance est financée par le crédit qui vous est fourni en vertu de votre contrat.</div>
                                </td>
                                <td className="p-[10px] border border-[#ddd] align-top">Le prix au comptant de votre police d'assurance est de {formatCurrency(premium)} et le prix total au comptant est de {formatCurrency(premium)}</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9]">
                                    Garantie requise
                                    <div className="text-[10px] text-[#6b7280] italic mt-1">Il s'agit d'une description de la garantie que vous devez fournir en relation avec le contrat de crédit.</div>
                                </td>
                                <td className="p-[10px] border border-[#ddd] align-top">Vous nous cédez la police d'assurance à laquelle le crédit se rapporte, ainsi que vos droits en vertu de la police.</td>
                            </tr>
                        </tbody>
                    </table>

                    {/* Section 3: Costs */}
                    <h2 className="text-[14px] font-bold text-[#003da5] mt-[20px] mb-[10px]">3. Coûts du crédit</h2>
                    <table className="w-full border-collapse mb-4 text-[12px]">
                        <tbody>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9] w-[35%]">Les taux d'intérêt qui s'appliquent au contrat de crédit</td>
                                <td className="p-[10px] border border-[#ddd] align-top">Taux d'intérêt simple fixe de {insuranceLevy}%. Les intérêts sont calculés en appliquant un taux simple fixe de {insuranceLevy}% à l'avance sur le montant total du crédit et en l'ajoutant immédiatement au solde dû. Le montant des intérêts ainsi calculé et appliqué sera payable dans chaque mensualité.</td>
                            </tr>
                            <tr>
                                <td className="p-[10px] border border-[#ddd] font-bold bg-[#f9f9f9]">
                                    Taux Annuel Effectif Global (TAEG)
                                    <div className="text-[10px] text-[#6b7280] italic mt-1">Il s'agit du coût total exprimé en pourcentage annuel du montant total du crédit. Le TAEG vous aide à comparer différentes offres.</div>
                                </td>
                                <td className="p-[10px] border border-[#ddd] align-top">21,1%</td>
                            </tr>
                        </tbody>
                    </table>

                    {/* Footer Date */}
                    <div className="mt-[30px] pt-[15px] border-t-2 border-[#003da5] text-[11px] text-[#666]">
                        Document généré le : {new Date().toLocaleDateString('fr-FR')}
                    </div>
                </div>
            </div>
        </div>
    );
}
