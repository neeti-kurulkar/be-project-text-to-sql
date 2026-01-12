import { useState } from 'react';
import { TABLES, MOCK_TABLE_DATA } from '../../utils/mockData';
import { Select } from '../common/Select';
import { TableView } from './TableView';
import { Card } from '../common/Card';

export function TableBrowser() {
  const [selectedTable, setSelectedTable] = useState(TABLES[0].name);

  const tableOptions = TABLES.map((table) => ({
    value: table.name,
    label: `${table.displayName} (${table.rowCount.toLocaleString()} rows)`
  }));

  const currentTable = TABLES.find((t) => t.name === selectedTable);
  const tableData = MOCK_TABLE_DATA[selectedTable] || [];

  return (
    <Card title="Table Browser" description="Browse raw database tables">
      <div className="space-y-4">
        <Select
          label="Select Table"
          options={tableOptions}
          value={selectedTable}
          onChange={setSelectedTable}
        />

        {currentTable && (
          <TableView
            tableName={currentTable.displayName}
            data={tableData}
            totalRows={currentTable.rowCount}
          />
        )}
      </div>
    </Card>
  );
}
