<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Client;

class ClientController extends Controller
{
    public function index()
    {
        // Load clients and their printer counts
        $clients = Client::withCount('printers')->orderBy('name')->get();
        return view('clients.index', compact('clients'));
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255|unique:clients,name',
        ]);

        Client::create($validated);

        return redirect()->route('clients.index')->with('success', 'Cliente cadastrado com sucesso!');
    }

    public function destroy(Client $client)
    {
        // Because of cascade on delete, this will also drop their locations history if we configured it correctly.
        // For printers currently assigned to this client, we should probably set them to null.
        // Actually, the migration `nullOnDelete` handles setting the printer's `client_id` to null!
        
        $client->delete();

        return redirect()->route('clients.index')->with('success', 'Cliente removido com sucesso!');
    }
}
