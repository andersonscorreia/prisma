<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>G Trigueiro - Relatórios de Faturamento</title>
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
</head>
<body class="bg-gray-50 text-gray-800 font-sans antialiased">

    <!-- Navbar -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center space-x-8">
                    <div class="flex-shrink-0 flex items-center">
                        <div class="w-10 h-10 bg-brand rounded flex items-center justify-center text-white font-bold text-xl mr-3">
                            GT
                        </div>
                        <span class="font-bold text-xl text-gray-900 tracking-tight">Monitoramento</span>
                    </div>
                    <div class="hidden md:flex space-x-4">
                        <a href="{{ route('dashboard') }}" class="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors">Equipamentos</a>
                        <a href="{{ route('clients.index') }}" class="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors">Clientes</a>
                        <a href="{{ route('reports.index') }}" class="text-brand px-3 py-2 rounded-md text-sm font-medium transition-colors border-b-2 border-brand">Relatórios Mês</a>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        
        <div class="md:flex md:items-center md:justify-between mb-8">
            <div class="flex-1 min-w-0">
                <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl">Relatório de Faturamento Mensal</h2>
                <p class="mt-1 text-sm text-gray-500">Volume de impressões contabilizado para o mês selecionado.</p>
            </div>
            
            <!-- Filter Form -->
            <div class="mt-4 flex md:mt-0 md:ml-4 bg-white p-2 rounded-lg shadow-sm border border-gray-200">
                <form method="GET" action="{{ route('reports.index') }}" class="flex flex-wrap items-center gap-3">
                    <div>
                        <select name="client_id" class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-brand focus:border-brand sm:text-sm rounded-md bg-gray-50 max-w-[200px]">
                            <option value="">Todos os Clientes</option>
                            @foreach($clients as $c)
                                <option value="{{ $c->id }}" {{ $clientId == $c->id ? 'selected' : '' }}>{{ $c->name }}</option>
                            @endforeach
                        </select>
                    </div>
                    <div>
                        <select name="printer_id" class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-brand focus:border-brand sm:text-sm rounded-md bg-gray-50 max-w-[200px]">
                            <option value="">Todas Impressoras</option>
                            @foreach($printersList as $p)
                                <option value="{{ $p->id }}" {{ $printerId == $p->id ? 'selected' : '' }}>{{ $p->name }}</option>
                            @endforeach
                        </select>
                    </div>
                    <div>
                        <select name="month" class="block w-full pl-3 pr-8 py-2 text-base border-gray-300 focus:outline-none focus:ring-brand focus:border-brand sm:text-sm rounded-md bg-gray-50">
                            @for($i = 1; $i <= 12; $i++)
                                <option value="{{ $i }}" {{ $month == $i ? 'selected' : '' }}>
                                    Mês {{ str_pad($i, 2, '0', STR_PAD_LEFT) }}
                                </option>
                            @endfor
                        </select>
                    </div>
                    <div>
                        <select name="year" class="block w-full pl-3 pr-8 py-2 text-base border-gray-300 focus:outline-none focus:ring-brand focus:border-brand sm:text-sm rounded-md bg-gray-50">
                            @for($y = now()->year; $y >= now()->year - 2; $y--)
                                <option value="{{ $y }}" {{ $year == $y ? 'selected' : '' }}>{{ $y }}</option>
                            @endfor
                        </select>
                    </div>
                    <button type="submit" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-brand hover:bg-brand-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand transition-colors">
                        Filtrar
                    </button>
                    <button type="button" onclick="window.print()" class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none transition-colors">
                        Imprimir
                    </button>
                </form>
            </div>
        </div>

        <!-- Table -->
        <div class="flex flex-col">
            <div class="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
                <div class="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
                    <div class="shadow-sm overflow-hidden border-b border-gray-200 sm:rounded-lg">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Cliente / Local</th>
                                    <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Equipamento</th>
                                    <th scope="col" class="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">1ª Leitura</th>
                                    <th scope="col" class="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">Última Leitura</th>
                                    <th scope="col" class="px-6 py-3 text-right text-xs font-bold text-white bg-brand rounded-t-md uppercase tracking-wider tracking-wider" style="max-width:150px">Volume Cobrado</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-200">
                                @forelse($reportData as $row)
                                    <tr class="hover:bg-gray-50 transition-colors">
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm font-bold text-gray-900">{{ $row['client'] ? $row['client']->name : 'Estoque / Sem Cliente' }}</div>
                                            <div class="text-xs text-gray-400">
                                                {{ $row['period_start']->format('d/m') }} até {{ $row['period_end']->format('d/m/Y') }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm font-semibold text-gray-900">{{ $row['printer']->name ?: 'Sem Nome' }}</div>
                                            <div class="text-xs text-brand uppercase">{{ $row['printer']->model }} (Série: {{ $row['printer']->serial_number }})</div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right font-mono">
                                            {{ $row['first_counter'] !== 'N/D' ? number_format($row['first_counter'], 0, ',', '.') : 'N/D' }}
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right font-mono">
                                            {{ $row['last_counter'] !== 'N/D' ? number_format($row['last_counter'], 0, ',', '.') : 'N/D' }}
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-right font-bold text-lg text-gray-900 
                                            {{ !$row['has_data'] ? 'text-gray-300' : '' }}">
                                            {{ $row['has_data'] ? number_format($row['pages_printed'], 0, ',', '.') : '-' }}
                                        </td>
                                    </tr>
                                @empty
                                    <tr>
                                        <td colspan="5" class="px-6 py-10 whitespace-nowrap text-sm text-gray-500 text-center">
                                            Nenhum equipamento cadastrado no sistema.
                                        </td>
                                    </tr>
                                @endforelse
                                
                                @if(count($reportData) > 0)
                                    <!-- Totals Footer -->
                                    <tr class="bg-gray-50 font-bold border-t-2 border-gray-300">
                                        <td colspan="4" class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right uppercase tracking-wider">
                                            Total Geral (Mês):
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-right text-xl text-brand">
                                            {{ number_format(collect($reportData)->sum('pages_printed'), 0, ',', '.') }}
                                        </td>
                                    </tr>
                                @endif

                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
    </main>
</body>
</html>
