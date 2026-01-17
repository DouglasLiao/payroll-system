import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
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
  // Pagination props
  totalCount?: number
  page?: number
  rowsPerPage?: number
  onPageChange?: (page: number) => void
  onRowsPerPageChange?: (rowsPerPage: number) => void
  rowsPerPageOptions?: number[]
}

export function GenericTable<T>({
  data,
  columns,
  keyExtractor,
  emptyMessage = 'No data available',
  loading = false,
  totalCount,
  page = 0,
  rowsPerPage = 10,
  onPageChange,
  onRowsPerPageChange,
  rowsPerPageOptions = [5, 10, 25, 50],
}: GenericTableProps<T>) {
  const handleChangePage = (_event: unknown, newPage: number) => {
    onPageChange?.(newPage)
  }

  const handleChangeRowsPerPage = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    onRowsPerPageChange?.(parseInt(event.target.value, 10))
  }

  return (
    <Paper sx={{ width: '100%' }}>
      <TableContainer>
        <Table sx={{ width: '100%' }}>
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
                      <Skeleton animation="wave" height={30} variant="text" />
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
      {totalCount !== undefined && onPageChange && onRowsPerPageChange && (
        <TablePagination
          rowsPerPageOptions={rowsPerPageOptions}
          component="div"
          count={totalCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      )}
    </Paper>
  )
}
