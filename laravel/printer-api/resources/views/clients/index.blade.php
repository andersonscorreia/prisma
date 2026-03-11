<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>G Trigueiro - Clientes</title>
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
                        <a href="{{ route('clients.index') }}" class="text-brand px-3 py-2 rounded-md text-sm font-medium transition-colors border-b-2 border-brand">Clientes</a>
                        <a href="{{ route('reports.index') }}" class="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors">Relatórios Mês</a>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        
        <div class="md:flex md:items-center md:justify-between mb-8">
            <div class="flex-1 min-w-0">
                <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl">Gestão de Clientes</h2>
                <p class="mt-1 text-sm text-gray-500">Cadastre os locais onde seus equipamentos estão locados.</p>
            </div>
        </div>

        @if(session('success'))
            <div class="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-6" role="alert">
                <p>{{ session('success') }}</p>
            </div>
        @endif

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Form to Add Client -->
            <div class="lg:col-span-1">
                <div class="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
                    <div class="p-6 border-b border-gray-200 bg-gray-50">
                        <h3 class="text-lg font-bold text-gray-900">Novo Cliente</h3>
                    </div>
                    <div class="p-6">
                        <form action="{{ route('clients.store') }}" method="POST">
                            @csrf
                            <div class="mb-4">
                                <label for="name" class="block text-sm font-medium text-gray-700">Nome / Razão Social</label>
                                <input type="text" name="name" id="name" required class="mt-1 p-2 focus:ring-brand focus:border-brand block w-full shadow-sm sm:text-sm border-gray-300 rounded-md bg-gray-50 border" placeholder="Ex: Clínica São José">
                                @error('name')
                                    <p class="text-red-500 text-xs mt-1">{{ $message }}</p>
                                @enderror
                            </div>
                            <button type="submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-brand hover:bg-brand-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand">
                                Cadastrar Cliente
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- List of Clients -->
            <div class="lg:col-span-2">
                <div class="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
                    <ul class="divide-y divide-gray-200">
                        @forelse($clients as $client)
                            <li class="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
                                <div>
                                    <p class="text-sm font-bold text-gray-900">{{ $client->name }}</p>
                                    <p class="text-xs text-gray-500 mt-1">
                                        {{ $client->printers_count }} {{ $client->printers_count === 1 ? 'equipamento vinculado' : 'equipamentos vinculados' }}
                                    </p>
                                </div>
                                <div>
                                    <form action="{{ route('clients.destroy', $client->id) }}" method="POST" onsubmit="return confirm('Tem certeza que deseja excluir este cliente?');">
                                        @csrf
                                        @method('DELETE')
                                        <button type="submit" class="text-red-500 hover:text-red-700 text-sm font-medium">Excluir</button>
                                    </form>
                                </div>
                            </li>
                        @empty
                            <li class="px-6 py-8 text-center text-gray-500 text-sm">
                                Nenhum cliente cadastrado ainda.
                            </li>
                        @endforelse
                    </ul>
                </div>
            </div>
        </div>
        
    </main>
</body>
</html>
