<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>G Trigueiro - Monitoramento de Impressoras</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        brand: {
                            DEFAULT: '#E3262E',
                            dark: '#c11b22',
                        }
                    }
                }
            }
        }
    </script>
    <style>
        .filter-btn.active {
            background-color: #E3262E;
            color: white;
            border-color: #E3262E;
        }
    </style>
</head>
<body class="bg-gray-50 text-gray-800 font-sans antialiased">

    <!-- Navbar -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <div class="flex-shrink-0 flex items-center">
                        <div class="w-10 h-10 bg-brand rounded flex items-center justify-center text-white font-bold text-xl mr-3">
                            GT
                        </div>
                        <span class="font-bold text-xl text-gray-900 tracking-tight">Monitoramento Técnico</span>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="text-sm font-medium text-gray-500">
                        Última atualização: <span id="last-refresh" class="text-gray-900">{{ now()->format('H:i:s') }}</span>
                    </div>
                    <button onclick="window.location.reload()" class="p-2 rounded-md text-gray-400 hover:text-brand hover:bg-gray-100 transition-colors">
                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <!-- Header & Filters -->
        <div class="md:flex md:items-center md:justify-between mb-8">
            <div class="flex-1 min-w-0">
                <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">Painel de Equipamentos</h2>
                <p class="mt-1 text-sm text-gray-500">Visão geral técnica e níveis de suprimento</p>
            </div>
            <div class="mt-4 flex md:mt-0 md:ml-4 space-x-2" id="filter-container">
                <button type="button" data-filter="all" class="filter-btn active inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none transition-colors">
                    Todos
                </button>
                <button type="button" data-filter="canon" class="filter-btn inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none transition-colors">
                    Canon
                </button>
                <button type="button" data-filter="ricoh" class="filter-btn inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none transition-colors">
                    Ricoh
                </button>
                <button type="button" data-filter="epson" class="filter-btn inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none transition-colors">
                    Epson
                </button>
            </div>
        </div>

        <!-- Grid de Impressoras -->
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3" id="printers-grid">
            @forelse ($printers as $printer)
                @php
                    // Determina se está online baseado no updated_at (menor que 15 min)
                    $isOnline = $printer->updated_at->diffInMinutes(now()) <= 15;
                    $statusColor = $isOnline ? 'bg-green-100 text-green-800 border-green-200' : 'bg-red-100 text-red-800 border-red-200';
                    $statusDot = $isOnline ? 'bg-green-500' : 'bg-red-500';
                    $statusText = $isOnline ? 'Online' : 'Offline';
                    
                    // Extrai a marca (simplificado baseado no nome/modelo para o filtro)
                    $searchString = strtolower($printer->name . ' ' . $printer->model);
                    $brand = 'outros';
                    if (str_contains($searchString, 'canon')) $brand = 'canon';
                    elseif (str_contains($searchString, 'ricoh')) $brand = 'ricoh';
                    elseif (str_contains($searchString, 'epson')) $brand = 'epson';
                @endphp

                <div class="printer-card bg-white overflow-hidden shadow-sm rounded-xl border border-gray-200 hover:shadow-md transition-shadow relative" data-brand="{{ $brand }}">
                    <!-- Faixa superior da marca/red -->
                    <div class="h-1 bg-brand w-full absolute top-0 left-0"></div>
                    
                    <div class="p-6">
                        <!-- Header do Card -->
                        <div class="flex justify-between items-start mb-4">
                            <div class="pr-3">
                                <h3 class="text-lg font-bold text-gray-900 leading-tight">{{ $printer->name ?: 'Equipamento ID '.$printer->id }}</h3>
                                <p class="text-xs font-medium text-brand mt-1 uppercase tracking-wider">{{ $printer->model ?: 'Modelo Desconhecido' }}</p>
                            </div>
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border {{ $statusColor }}">
                                <span class="w-2 h-2 mr-1.5 rounded-full {{ $statusDot }}"></span>
                                {{ $statusText }}
                            </span>
                        </div>

                        <!-- Dados Técnicos -->
                        <div class="bg-gray-50 rounded-lg p-3 mb-5 border border-gray-100">
                            <div class="grid grid-cols-2 gap-y-2 gap-x-4 text-sm">
                                <div>
                                    <span class="block text-xs text-gray-500 font-medium">Série</span>
                                    <span class="block text-gray-900 font-semibold font-mono">{{ $printer->serial_number }}</span>
                                </div>
                                <div>
                                    <span class="block text-xs text-gray-500 font-medium">IP</span>
                                    <span class="block text-gray-900 font-semibold font-mono">{{ $printer->ip_address ?: 'N/D' }}</span>
                                </div>
                                <div class="col-span-2 mt-1 pt-2 border-t border-gray-200">
                                    <span class="block text-xs text-gray-500 font-medium mb-1">Contador Físico</span>
                                    <div class="font-mono text-xl text-gray-900 font-bold tracking-tight">
                                        {{ number_format($printer->last_counter, 0, ',', '.') }}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Níveis de Toner -->
                        <div>
                            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Suprimentos</h4>
                            
                            @if(is_array($printer->last_toner_data) && count($printer->last_toner_data) > 0)
                                <div class="space-y-3">
                                    @foreach($printer->last_toner_data as $toner)
                                        @php
                                            $level = max(0, min(100, (int)($toner['level'] ?? 0)));
                                            
                                            // Lógica de cores baseada em thresholds de suprimento
                                            if ($level > 50) {
                                                $barColor = 'bg-green-500';
                                                $textColor = 'text-green-700';
                                            } elseif ($level > 15) {
                                                $barColor = 'bg-yellow-400';
                                                $textColor = 'text-yellow-700';
                                            } else {
                                                $barColor = 'bg-red-500';
                                                $textColor = 'text-red-700';
                                            }
                                        @endphp
                                        <div>
                                            <div class="flex justify-between items-end mb-1">
                                                <span class="text-xs font-semibold text-gray-700">{{ $toner['color'] ?? 'Desconhecido' }}</span>
                                                <span class="text-xs font-bold {{ $textColor }}">{{ $level }}%</span>
                                            </div>
                                            <div class="w-full bg-gray-200 rounded-full h-2">
                                                <div class="{{ $barColor }} h-2 rounded-full transition-all duration-1000 ease-out" style="width: {{ $level }}%"></div>
                                            </div>
                                        </div>
                                    @endforeach
                                </div>
                            @else
                                <div class="text-center py-4 bg-gray-50 rounded border border-dashed border-gray-300 text-gray-400 text-xs">
                                    Nenhum dado de suprimento registrado.
                                </div>
                            @endif
                        </div>
                    </div>
                    
                    <div class="bg-gray-50 border-t border-gray-200 px-6 py-3">
                        <div class="text-xs text-gray-500 flex justify-between items-center mb-3">
                            <span>Recebido: {{ $printer->updated_at->diffForHumans() }}</span>
                            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        </div>
                        
                        <!-- Agent Sync Controls -->
                        <div class="flex items-center justify-between border-t border-gray-200 pt-3 mt-1">
                            <div class="flex items-center">
                                <label for="interval-{{ $printer->id }}" class="text-xs font-medium text-gray-600 mr-2">Sync:</label>
                                <select id="interval-{{ $printer->id }}" data-id="{{ $printer->id }}" class="sync-interval text-xs border-gray-300 rounded-md shadow-sm focus:ring-brand focus:border-brand py-1 pl-2 pr-6">
                                    <option value="5" {{ $printer->check_interval == 5 ? 'selected' : '' }}>5 min</option>
                                    <option value="15" {{ $printer->check_interval == 15 ? 'selected' : '' }}>15 min</option>
                                    <option value="30" {{ $printer->check_interval == 30 ? 'selected' : '' }}>30 min</option>
                                    <option value="60" {{ $printer->check_interval == 60 ? 'selected' : '' }}>1 hora</option>
                                </select>
                            </div>
                            <button type="button" data-id="{{ $printer->id }}" class="force-update-btn inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-brand bg-red-100 hover:bg-red-200 focus:outline-none transition-colors">
                                Atualizar Agora
                            </button>
                        </div>
                    </div>
                </div>
            @empty
                <div class="col-span-full bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                    <svg class="mx-auto h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                    </svg>
                    <h3 class="mt-2 text-sm font-medium text-gray-900">Sem equipamentos</h3>
                    <p class="mt-1 text-sm text-gray-500">Nenhum dado foi recebido pelo Agente Python ainda.</p>
                </div>
            @endforelse
        </div>
    </main>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const buttons = document.querySelectorAll('.filter-btn');
            const cards = document.querySelectorAll('.printer-card');

            buttons.forEach(btn => {
                btn.addEventListener('click', () => {
                    // Atualiza estado ativo dos botões
                    buttons.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');

                    // Pega o filtro selecionado
                    const filter = btn.getAttribute('data-filter');

                    // Mostra/esconde cards
                    cards.forEach(card => {
                        if (filter === 'all' || card.getAttribute('data-brand') === filter) {
                            card.style.display = 'block';
                            // Animacao suave de entrada
                            card.style.opacity = '0';
                            setTimeout(() => {
                                card.style.transition = 'opacity 0.3s ease-in';
                                card.style.opacity = '1';
                            }, 10);
                        } else {
                            card.style.display = 'none';
                        }
                    });
                });
            });

            // Agent Sync Logic (AJAX)
            const csrfToken = '{{ csrf_token() }}';

            document.querySelectorAll('.sync-interval').forEach(select => {
                select.addEventListener('change', function() {
                    const printerId = this.getAttribute('data-id');
                    const interval = this.value;
                    
                    this.disabled = true;
                    this.classList.add('opacity-50');

                    fetch(`/dashboard/printers/${printerId}/config`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRF-TOKEN': csrfToken,
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify({ check_interval: interval })
                    })
                    .then(response => response.json())
                    .then(data => {
                        this.disabled = false;
                        this.classList.remove('opacity-50');
                        // Feedback opcional de sucesso
                        this.style.borderColor = '#16a34a'; // tailwind green-600
                        setTimeout(() => this.style.borderColor = '', 2000);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        this.disabled = false;
                        this.classList.remove('opacity-50');
                        alert('Erro ao salvar intervalo.');
                    });
                });
            });

            document.querySelectorAll('.force-update-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const printerId = this.getAttribute('data-id');
                    const originalText = this.innerText;
                    
                    this.disabled = true;
                    this.innerText = 'Enviando...';
                    this.classList.add('opacity-50');

                    fetch(`/dashboard/printers/${printerId}/config`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRF-TOKEN': csrfToken,
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify({ force_update: true })
                    })
                    .then(response => response.json())
                    .then(data => {
                        this.innerText = 'Comando Enviado!';
                        this.classList.remove('bg-red-100', 'text-brand');
                        this.classList.add('bg-green-100', 'text-green-800');
                        
                        setTimeout(() => {
                            this.disabled = false;
                            this.innerText = originalText;
                            this.classList.remove('opacity-50', 'bg-green-100', 'text-green-800');
                            this.classList.add('bg-red-100', 'text-brand');
                        }, 3000);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        this.disabled = false;
                        this.innerText = originalText;
                        this.classList.remove('opacity-50');
                        alert('Erro ao enviar comando.');
                    });
                });
            });
        });
    </script>
</body>
</html>
