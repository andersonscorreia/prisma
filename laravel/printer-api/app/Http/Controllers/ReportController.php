<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Printer;
use Carbon\Carbon;

class ReportController extends Controller
{
    public function index(Request $request)
    {
        $month = $request->input('month', now()->month);
        $year = $request->input('year', now()->year);
        $clientId = $request->input('client_id');
        $printerId = $request->input('printer_id');

        $startDate = Carbon::createFromDate($year, $month, 1)->startOfMonth();
        $endDate = $startDate->copy()->endOfMonth();

        $clients = \App\Models\Client::orderBy('name')->get();
        $printersList = Printer::orderBy('name')->get();

        // Find all location assignments that were active during this month
        $locationsQuery = \App\Models\PrinterLocation::with(['printer', 'client'])
            ->where('installed_at', '<=', $endDate)
            ->where(function ($q) use ($startDate) {
                $q->whereNull('removed_at')
                  ->orWhere('removed_at', '>=', $startDate);
            });

        if ($clientId) {
            $locationsQuery->where('client_id', $clientId);
        }
        if ($printerId) {
            $locationsQuery->where('printer_id', $printerId);
        }

        $locations = $locationsQuery->get();
        $reportData = [];

        foreach ($locations as $location) {
            if (!$location->printer) continue;

            // Determine the exact timeframe this printer was at this client inside this specific month
            $periodStart = $location->installed_at > $startDate ? $location->installed_at : $startDate;
            $periodEnd = $location->removed_at && $location->removed_at < $endDate ? $location->removed_at : $endDate;

            $firstCounter = $location->printer->counters()
                ->whereBetween('recorded_at', [$periodStart, $periodEnd])
                ->orderBy('recorded_at', 'asc')
                ->first();

            $lastCounter = $location->printer->counters()
                ->whereBetween('recorded_at', [$periodStart, $periodEnd])
                ->orderBy('recorded_at', 'desc')
                ->first();

            $pagesPrinted = 0;
            if ($firstCounter && $lastCounter) {
                $pagesPrinted = $lastCounter->counter - $firstCounter->counter;
            }

            $reportData[] = [
                'printer' => $location->printer,
                'client' => $location->client,
                'first_counter' => $firstCounter ? $firstCounter->counter : 'N/D',
                'last_counter' => $lastCounter ? $lastCounter->counter : 'N/D',
                'pages_printed' => $pagesPrinted,
                'has_data' => ($firstCounter && $lastCounter),
                'period_start' => $periodStart,
                'period_end' => $periodEnd,
            ];
        }

        // Also fetch printers that have NO location history ever, if no filters are applied
        if (!$clientId) {
            $unassignedPrinters = Printer::doesntHave('locations')->get();
            if ($printerId) {
                $unassignedPrinters = $unassignedPrinters->where('id', $printerId);
            }

            foreach ($unassignedPrinters as $printer) {
                $firstCounter = $printer->counters()
                    ->whereBetween('recorded_at', [$startDate, $endDate])
                    ->orderBy('recorded_at', 'asc')
                    ->first();

                $lastCounter = $printer->counters()
                    ->whereBetween('recorded_at', [$startDate, $endDate])
                    ->orderBy('recorded_at', 'desc')
                    ->first();

                $pagesPrinted = 0;
                if ($firstCounter && $lastCounter) $pagesPrinted = $lastCounter->counter - $firstCounter->counter;

                $reportData[] = [
                    'printer' => $printer,
                    'client' => null,
                    'first_counter' => $firstCounter ? $firstCounter->counter : 'N/D',
                    'last_counter' => $lastCounter ? $lastCounter->counter : 'N/D',
                    'pages_printed' => $pagesPrinted,
                    'has_data' => ($firstCounter && $lastCounter),
                    'period_start' => clone $startDate,
                    'period_end' => clone $endDate,
                ];
            }
        }

        return view('reports.index', compact('reportData', 'month', 'year', 'startDate', 'clients', 'printersList', 'clientId', 'printerId'));
    }
}
