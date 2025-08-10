"use client";

import { useParams } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
  type SortingState,
  type RowSelectionState,
} from "@tanstack/react-table";
import { useMemo, useState, useRef, useEffect } from "react";
import api from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

// Define data types
type Page = {
  id: number;
  url: string;
  status_code: number | null;
  page_elements: { title: string | null; h1: string | null; } | null;
};

type Template = {
  id: number;
  name: string;
};

function IndeterminateCheckbox({
  indeterminate,
  className = '',
  ...rest
}: { indeterminate?: boolean } & React.HTMLProps<HTMLInputElement>) {
  const ref = useRef<HTMLInputElement>(null!)

  useEffect(() => {
    if (typeof indeterminate === 'boolean') {
      ref.current.indeterminate = !rest.checked && indeterminate
    }
  }, [ref, indeterminate, rest.checked])

  return (
    <input
      type="checkbox"
      ref={ref}
      className={className + ' cursor-pointer'}
      {...rest}
    />
  )
}

// Define columns
const columnHelper = createColumnHelper<Page>();

export default function SitePage() {
  const params = useParams<{ siteId: string }>();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [columnVisibility, setColumnVisibility] = useState({});
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<string>("");

  // Data fetching for pages
  const { data, isLoading, error } = useQuery({
    queryKey: ["sitePages", params.siteId],
    queryFn: async () => {
      const response = await api.get(`/sites/${params.siteId}/pages?size=1000`);
      return response.data;
    },
    enabled: !!user,
  });

  // Data fetching for templates
  const { data: templates } = useQuery<Template[]>({
    queryKey: ["templates", user?.org_id],
    queryFn: async () => {
        if (!user) return [];
        const response = await api.get(`/templates/org/${user.org_id}`);
        return response.data;
    },
    enabled: !!user && isModalOpen, // Only fetch when modal is open
  });

  // Mutation for running a prompt
  const runPromptMutation = useMutation({
    mutationFn: ({ pageId, templateId }: { pageId: number, templateId: number }) => {
      return api.post(`/prompts/run/page/${pageId}`, { template_id: templateId });
    },
    onSuccess: () => {
      // In a real app, you might want to show a success notification
      console.log("Prompt execution started.");
    },
  });

  const handleRunPrompt = () => {
    const templateId = parseInt(selectedTemplate, 10);
    if (!templateId) {
      alert("Please select a template.");
      return;
    }
    const selectedPageIds = Object.keys(rowSelection).map(Number);
    selectedPageIds.forEach(pageId => {
      runPromptMutation.mutate({ pageId, templateId });
    });
    setIsModalOpen(false);
    setRowSelection({});
  };

  const handleExport = async () => {
    try {
      const response = await api.get(`/export/site/${params.siteId}/csv`, {
        responseType: 'blob', // Important
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const filename = `site_${params.siteId}_export.csv`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to export CSV", error);
      alert("Failed to download CSV.");
    }
  };

  const columns = useMemo(() => [
    {
      id: 'select',
      header: ({ table }) => (
        <IndeterminateCheckbox
          {...{
            checked: table.getIsAllRowsSelected(),
            indeterminate: table.getIsSomeRowsSelected(),
            onChange: table.getToggleAllRowsSelectedHandler(),
          }}
        />
      ),
      cell: ({ row }) => (
        <IndeterminateCheckbox
          {...{
            checked: row.getIsSelected(),
            disabled: !row.getCanSelect(),
            indeterminate: row.getIsSomeSelected(),
            onChange: row.getToggleSelectedHandler(),
          }}
        />
      ),
    },
    columnHelper.accessor("url", { header: "URL", cell: (info) => <a href={info.getValue()} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">{info.getValue()}</a> }),
    columnHelper.accessor((row) => row.page_elements?.title, { id: "title", header: "Title", cell: (info) => info.getValue() || "-" }),
    columnHelper.accessor((row) => row.page_elements?.h1, { id: "h1", header: "H1", cell: (info) => info.getValue() || "-" }),
    columnHelper.accessor("status_code", { header: "Status", cell: (info) => info.getValue() }),
  ], [params.siteId]);

  const table = useReactTable({
    data: data?.items ?? [],
    columns,
    state: { sorting, globalFilter, columnVisibility, rowSelection },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    enableRowSelection: true,
  });

  if (isLoading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-500">An error has occurred: {error.message}</div>;

  return (
    <div className="p-4">
      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
          <div className="bg-white p-6 rounded-lg shadow-xl">
            <h2 className="text-lg font-bold mb-4">Run a Prompt</h2>
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="w-full p-2 border rounded mb-4"
            >
              <option value="" disabled>Select a template...</option>
              {templates?.map(template => (
                <option key={template.id} value={template.id}>{template.name}</option>
              ))}
            </select>
            <div className="flex justify-end space-x-2">
              <button onClick={() => setIsModalOpen(false)} className="p-2 bg-gray-300 rounded">Cancel</button>
              <button onClick={handleRunPrompt} className="p-2 bg-blue-500 text-white rounded">Run</button>
            </div>
          </div>
        </div>
      )}

      <h1 className="text-2xl font-bold mb-4">Pages for Site {params.siteId}</h1>

      <div className="flex justify-between mb-4">
        <div className="flex items-center space-x-4">
            <input
              type="text"
              value={globalFilter}
              onChange={(e) => setGlobalFilter(e.target.value)}
              placeholder="Search all columns..."
              className="border p-2 rounded"
            />
            <button
              onClick={() => setIsModalOpen(true)}
              className="p-2 bg-green-500 text-white rounded disabled:bg-gray-400"
              disabled={Object.keys(rowSelection).length === 0}
            >
              Run Prompt ({Object.keys(rowSelection).length})
            </button>
            <button
                onClick={handleExport}
                className="p-2 bg-gray-600 text-white rounded"
            >
                Export CSV
            </button>
        </div>
        {/* ... Column Visibility ... */}
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
                    {{ asc: ' 🔼', desc: ' 🔽' }[header.column.getIsSorted() as string] ?? null}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {table.getRowModel().rows.map(row => (
              <tr key={row.id} className={row.getIsSelected() ? "bg-blue-100" : ""}>
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
