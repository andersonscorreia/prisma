<?php

namespace App\Http\Controllers;

use App\Models\Printer;
use Illuminate\Http\Request;

class PrinterController extends Controller
{
    public function index()
    {
        $printers = Printer::all();
        return view('printers.index', compact('printers'));
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
            'message' => 'Config updated successfully',
            'printer' => $printer
        ]);
    }
}
