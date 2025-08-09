"use client";

import { useQuery } from "@tanstack/react-query";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
  type SortingState,
} from "@tanstack/react-table";
import { useMemo, useState } from "react";

// Define the type for our Page data
type Page = {
  id: number;
  url: string;
  status_code: number | null;
  page_elements: {
    title: string | null;
    h1: string | null;
  } | null;
};

// Define columns using the column helper
const columnHelper = createColumnHelper<Page>();

export default function SitePage({ params }: { params: { siteId: string } }) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [columnVisibility, setColumnVisibility] = useState({});

  // Fetch data using react-query
  const { data, isLoading, error } = useQuery({
    queryKey: ["sitePages", params.siteId],
    queryFn: async () => {
      // In a real app, you'd have a proper API client.
      const res = await fetch(`/api/sites/${params.siteId}/pages?size=1000`); // Fetch more for client-side filtering
      if (!res.ok) {
        throw new Error(`Failed to fetch pages: ${res.statusText}`);
      }
      return res.json();
    },
  });

  const columns = useMemo(() => [
    columnHelper.accessor("url", {
      header: "URL",
      cell: (info) => <a href={info.getValue()} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">{info.getValue()}</a>,
    }),
    columnHelper.accessor((row) => row.page_elements?.title, {
      id: "title",
      header: "Title",
      cell: (info) => info.getValue() || "-",
    }),
    columnHelper.accessor((row) => row.page_elements?.h1, {
      id: "h1",
      header: "H1",
      cell: (info) => info.getValue() || "-",
    }),
    columnHelper.accessor("status_code", {
        header: "Status",
        cell: (info) => info.getValue(),
    }),
  ], []);

  const table = useReactTable({
    data: data?.items ?? [],
    columns,
    state: {
      sorting,
      globalFilter,
      columnVisibility,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  if (isLoading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-500">An error has occurred: {error.message}</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Pages for Site {params.siteId}</h1>

      <div className="flex justify-between mb-4">
        <input
          type="text"
          value={globalFilter}
          onChange={(e) => setGlobalFilter(e.target.value)}
          placeholder="Search all columns..."
          className="border p-2 rounded"
        />
        <div className="flex flex-wrap">
            {table.getAllLeafColumns().map(column => (
              <label key={column.id} className="inline-flex items-center mr-3">
                <input
                  {...{
                    type: 'checkbox',
                    checked: column.getIsVisible(),
                    onChange: column.getToggleVisibilityHandler(),
                  }}
                />
                <span className="ml-1">{column.id}</span>
              </label>
            ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th
                    key={header.id}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    {flexRender(header.column.columnDef.header, header.getContext())}
                    {{
                      asc: ' 🔼',
                      desc: ' 🔽',
                    }[header.column.getIsSorted() as string] ?? null}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {table.getRowModel().rows.map(row => (
              <tr key={row.id}>
                {row.getVisibleCells().map(cell => (
                  <td key={cell.id} className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
