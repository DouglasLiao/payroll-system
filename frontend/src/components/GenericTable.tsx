import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Skeleton,
} from '@mui/material'
import type { ReactNode } from 'react'

export interface Column<T> {
  id: string
  label: string
  // Provide either accessor (key of T) or render function
  accessor?: keyof T
  render?: (item: T) => ReactNode
  align?: 'left' | 'right' | 'center'
}

interface GenericTableProps<T> {
  data: T[] | undefined
  columns: Column<T>[]
  keyExtractor: (item: T) => string | number
  emptyMessage?: string
  loading?: boolean
}

export function GenericTable<T>({
  data,
  columns,
  keyExtractor,
  emptyMessage = 'No data available',
  loading = false,
}: GenericTableProps<T>) {
  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            {columns.map((col) => (
              <TableCell key={col.id} align={col.align || 'left'}>
                {col.label}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {loading ? (
            [...Array(5)].map((_, index) => (
              <TableRow key={index}>
                {columns.map((col) => (
                  <TableCell key={col.id}>
                    <Skeleton animation="wave" />
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : !data || data.length === 0 ? (
            <TableRow>
              <TableCell colSpan={columns.length} align="center" sx={{ py: 3 }}>
                <Typography color="textSecondary">{emptyMessage}</Typography>
              </TableCell>
            </TableRow>
          ) : (
            data.map((item) => (
              <TableRow key={keyExtractor(item)} hover>
                {columns.map((col) => (
                  <TableCell key={col.id} align={col.align || 'left'}>
                    {col.render
                      ? col.render(item)
                      : col.accessor
                        ? (item[col.accessor] as ReactNode)
                        : null}
                  </TableCell>
                ))}
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  )
}
