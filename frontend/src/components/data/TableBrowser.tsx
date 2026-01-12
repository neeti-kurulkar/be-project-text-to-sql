import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { listTables, getTableData } from '../../services/api';
import { Select } from '../common/Select';
import { TableView } from './TableView';
import { Card } from '../common/Card';

export function TableBrowser() {
  const [tables, setTables] = useState<any[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [tableData, setTableData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [dataLoading, setDataLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  // Fetch list of tables
  useEffect(() => {
    const fetchTables = async () => {
      try {
        setLoading(true);
        const data = await listTables();
        setTables(data);
        if (data.length > 0) {
          setSelectedTable(data[0].name);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load tables');
        console.error('Error fetching tables:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTables();
  }, []);

  // Fetch table data when selected table or page changes
  useEffect(() => {
    if (!selectedTable) return;

    const fetchTableData = async () => {
      try {
        setDataLoading(true);
        const data = await getTableData(selectedTable, currentPage, 50);
        setTableData(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load table data');
        console.error('Error fetching table data:', err);
      } finally {
        setDataLoading(false);
      }
    };
    fetchTableData();
  }, [selectedTable, currentPage]);

  const handleTableChange = (tableName: string) => {
    setSelectedTable(tableName);
    setCurrentPage(1); // Reset to first page when changing tables
  };

  if (loading) {
    return (
      <Card title="Table Browser" description="Browse raw database tables">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-electric-500" />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Table Browser" description="Browse raw database tables">
        <p className="text-red-600 dark:text-red-400">Error: {error}</p>
      </Card>
    );
  }

  const tableOptions = tables.map((table) => ({
    value: table.name,
    label: `${table.display_name} (${table.row_count.toLocaleString()} rows)`
  }));

  return (
    <Card title="Table Browser" description="Browse raw database tables">
      <div className="space-y-4">
        <Select
          label="Select Table"
          options={tableOptions}
          value={selectedTable}
          onChange={handleTableChange}
        />

        {dataLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-electric-500" />
          </div>
        ) : tableData ? (
          <TableView
            tableName={tableData.table_name}
            data={tableData.rows}
            totalRows={tableData.total_rows}
            currentPage={tableData.page}
            totalPages={tableData.total_pages}
            onPageChange={setCurrentPage}
          />
        ) : null}
      </div>
    </Card>
  );
}
