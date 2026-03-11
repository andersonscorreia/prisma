<?php

namespace App\Http\Controllers;

use App\Models\Printer;
use Illuminate\Http\Request;

class PrinterController extends Controller
{
    public function index()
    {
        $printers = Printer::all();
        $clients = \App\Models\Client::orderBy('name')->get();
        return view('printers.index', compact('printers', 'clients'));
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'serial_number' => 'required|string',
            'name' => 'nullable|string',
            'model' => 'nullable|string',
            'ip_address' => 'nullable|string',
            'last_counter' => 'nullable|integer',
            'last_toner_data' => 'nullable|array',
            'status' => 'nullable|string',
        ]);

        $printer = Printer::updateOrCreate(
            ['serial_number' => $validated['serial_number']],
            $validated
        );

        // Track counter history if it was provided
        if (isset($validated['last_counter'])) {
            $latestCounter = $printer->counters()->orderByDesc('recorded_at')->first();
            
            // Only insert a new history record if the counter changed (or it's the first time)
            if (!$latestCounter || $latestCounter->counter !== $validated['last_counter']) {
                $printer->counters()->create([
                    'counter' => $validated['last_counter'],
                    'recorded_at' => now(),
                ]);
            }
        }

        return response()->json([
            'message' => 'Printer data saved successfully',
            'printer' => $printer,
        ], 201);
    }
    public function getConfig($serial_number)
    {
        $printer = Printer::where('serial_number', $serial_number)->first();

        if (!$printer) {
            return response()->json(['message' => 'Printer not found'], 404);
        }

        $config = [
            'check_interval' => $printer->check_interval,
            'force_update' => $printer->force_update,
        ];

        // Reset force_update to false since the agent has picked it up
        if ($printer->force_update) {
            $printer->update(['force_update' => false]);
        }

        return response()->json($config);
    }

    public function updateConfig(Request $request, $id)
    {
        $printer = Printer::findOrFail($id);

        $validated = $request->validate([
            'check_interval' => 'nullable|integer|in:5,15,30,60',
            'force_update' => 'nullable|boolean',
        ]);

        if (isset($validated['check_interval'])) {
            $printer->check_interval = $validated['check_interval'];
        }

        if (isset($validated['force_update'])) {
            $printer->force_update = $validated['force_update'];
        }

        $printer->save();

        return response()->json([
            'message' => 'Configuration updated successfully'
        ]);
    }

    public function assignClient(Request $request, Printer $printer)
    {
        $validated = $request->validate([
            'client_id' => 'required|exists:clients,id',
        ]);

        $newClientId = $validated['client_id'];

        // Only do something if the client is actually changing
        if ($printer->client_id != $newClientId) {
            
            // 1. Close the current active location (if any)
            $activeLocation = $printer->locations()->whereNull('removed_at')->first();
            if ($activeLocation) {
                $activeLocation->update(['removed_at' => now()]);
            }

            // 2. Open a new location for the new client
            $printer->locations()->create([
                'client_id' => $newClientId,
                'installed_at' => now(),
            ]);

            // 3. Update the printer's current client pointer
            $printer->update(['client_id' => $newClientId]);
        }

        return redirect()->route('dashboard')->with('success', 'Cliente atribuído à impressora com sucesso!');
    }
}
