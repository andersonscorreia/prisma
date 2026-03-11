<script setup lang="ts">
import { Head } from '@inertiajs/vue3';
import AppLayout from '@/layouts/AppLayout.vue';

interface Printer {
    id: number;
    serial_number: string;
    name: string | null;
    model: string | null;
    ip_address: string | null;
    last_counter: number | null;
    last_toner_data: any[] | null;
    status: string | null;
    updated_at: string;
}

defineProps<{
    printers: Printer[];
}>();

const getTonerColor = (colorName: string) => {
    const lowercaseColor = colorName.toLowerCase();
    if (lowercaseColor.includes('black')) return 'bg-gray-900';
    if (lowercaseColor.includes('cyan')) return 'bg-cyan-500';
    if (lowercaseColor.includes('magenta')) return 'bg-pink-500';
    if (lowercaseColor.includes('yellow')) return 'bg-yellow-400';
    return 'bg-gray-400';
};
</script>

<template>
    <Head title="Monitoramento de Impressoras" />

    <AppLayout>
        <template #header>
            <h2 class="text-xl font-semibold leading-tight text-gray-800">
                Monitoramento de Impressoras
            </h2>
        </template>

        <div class="py-12 bg-gray-50 min-h-screen">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                <!-- Header Actions -->
                <div class="mb-6 flex justify-between items-center">
                    <h3 class="text-2xl font-bold text-gray-800">Status em Tempo Real</h3>
                    <div class="bg-white px-4 py-2 rounded shadow text-sm font-medium text-gray-600">
                        Total: {{ printers.length }} impressoras
                    </div>
                </div>

                <!-- Printer Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div v-for="printer in printers" :key="printer.id" 
                        class="bg-white overflow-hidden shadow-sm sm:rounded-lg border-t-4 border-[#E3262E] hover:shadow-md transition-shadow duration-200">
                        <div class="p-6">
                            <div class="flex justify-between items-start mb-4">
                                <div>
                                    <h4 class="text-lg font-bold text-gray-800">{{ printer.name || 'Impressora sem nome' }}</h4>
                                    <p class="text-sm text-gray-500">{{ printer.model || 'Modelo desconhecido' }}</p>
                                </div>
                                <span class="px-2 py-1 text-xs font-semibold rounded-full" 
                                      :class="printer.status === 'online' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'">
                                    {{ printer.status || 'Desconhecido' }}
                                </span>
                            </div>

                            <div class="mb-4 space-y-2">
                                <div class="flex justify-between text-sm">
                                    <span class="text-gray-500">Série:</span>
                                    <span class="font-medium text-gray-700">{{ printer.serial_number }}</span>
                                </div>
                                <div class="flex justify-between text-sm">
                                    <span class="text-gray-500">IP:</span>
                                    <span class="font-medium text-gray-700">{{ printer.ip_address || 'N/A' }}</span>
                                </div>
                                <div class="flex justify-between text-sm">
                                    <span class="text-gray-500">Contador:</span>
                                    <span class="font-medium text-gray-700">{{ printer.last_counter?.toLocaleString() || '0' }}</span>
                                </div>
                            </div>

                            <!-- Toner Levels -->
                            <div v-if="printer.last_toner_data && printer.last_toner_data.length > 0" class="mt-4 pt-4 border-t border-gray-100 space-y-3">
                                <h5 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Níveis de Toner</h5>
                                <div v-for="(toner, index) in printer.last_toner_data" :key="index" class="relative pt-1">
                                    <div class="flex mb-1 items-center justify-between">
                                        <div>
                                            <span class="text-xs font-semibold inline-block py-1 uppercase text-gray-600">
                                                {{ toner.color }}
                                            </span>
                                        </div>
                                        <div class="text-right">
                                            <span class="text-xs font-semibold inline-block text-gray-600">
                                                {{ toner.level }}%
                                            </span>
                                        </div>
                                    </div>
                                    <div class="overflow-hidden h-2 mb-2 text-xs flex rounded bg-gray-200">
                                        <div :style="`width: ${Math.max(0, Math.min(100, toner.level))}%`" 
                                             class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center transition-all duration-500"
                                             :class="getTonerColor(toner.color)">
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div v-else class="mt-4 pt-4 border-t border-gray-100">
                                <p class="text-xs text-center text-gray-400 italic">Sem dados de toner</p>
                            </div>

                            <div class="mt-4 pt-4 border-t border-gray-100 text-right">
                                <span class="text-xs text-gray-400">
                                    Atualizado em {{ new Date(printer.updated_at).toLocaleString('pt-BR') }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Empty State -->
                <div v-if="printers.length === 0" class="bg-white rounded-lg shadow-sm p-12 text-center border-t-4 border-[#E3262E]">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                    </svg>
                    <h3 class="mt-2 text-sm font-medium text-gray-900">Nenhuma impressora</h3>
                    <p class="mt-1 text-sm text-gray-500">Agentes de monitoramento ainda não enviaram dados.</p>
                </div>
            </div>
        </div>
    </AppLayout>
</template>
