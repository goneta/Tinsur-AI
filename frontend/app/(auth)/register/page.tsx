'use client';

import Link from 'next/link';
import { Button } from "@/components/ui/button";
import { Building2, UserCircle2 } from "lucide-react";

export default function RegisterPage() {
    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
            <div className="max-w-4xl w-full">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-black text-gray-900 mb-4">
                        Join Tinsur.AI
                    </h1>
                    <p className="text-gray-500 text-lg">
                        Choose how you would like to register
                    </p>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                    {/* Client Registration Card */}
                    <div className="bg-white rounded-[30px] p-8 border hover:border-blue-500 hover:shadow-xl transition-all group cursor-pointer relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <UserCircle2 className="w-32 h-32 text-blue-500" />
                        </div>
                        <div className="relative z-10 flex flex-col h-full">
                            <div className="bg-blue-50 w-16 h-16 rounded-2xl flex items-center justify-center mb-6 text-blue-600 group-hover:scale-110 transition-transform">
                                <UserCircle2 className="w-8 h-8" />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-2">Individual Client</h2>
                            <p className="text-gray-500 mb-8 flex-grow">
                                Join as an individual to manage your insurance policies, track claims, and get personalized coverage.
                            </p>
                            <Link href="/register/client" className="w-full">
                                <Button className="w-full h-12 rounded-xl text-lg font-bold bg-blue-600 hover:bg-blue-700">
                                    Register as Client
                                </Button>
                            </Link>
                        </div>
                    </div>

                    {/* Company Registration Card */}
                    <div className="bg-white rounded-[30px] p-8 border hover:border-purple-500 hover:shadow-xl transition-all group cursor-pointer relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Building2 className="w-32 h-32 text-purple-500" />
                        </div>
                        <div className="relative z-10 flex flex-col h-full">
                            <div className="bg-purple-50 w-16 h-16 rounded-2xl flex items-center justify-center mb-6 text-purple-600 group-hover:scale-110 transition-transform">
                                <Building2 className="w-8 h-8" />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-2">Insurance Company</h2>
                            <p className="text-gray-500 mb-8 flex-grow">
                                Register your insurance company to manage clients, issue policies, and streamline your operations.
                            </p>
                            <Link href="/register/company" className="w-full">
                                <Button className="w-full h-12 rounded-xl text-lg font-bold bg-white text-purple-600 border-2 border-purple-100 hover:bg-purple-50 hover:border-purple-200">
                                    Register as Company
                                </Button>
                            </Link>
                        </div>
                    </div>
                </div>

                <div className="text-center mt-12">
                    <p className="text-gray-500">
                        Already have an account?{' '}
                        <Link href="/login" className="text-blue-600 font-bold hover:underline">
                            Login here
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
