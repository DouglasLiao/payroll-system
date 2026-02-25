import { useSnackbar, type OptionsObject } from 'notistack'

export const useToast = () => {
  const { enqueueSnackbar } = useSnackbar()

  const toast = {
    success: (message: string, options?: OptionsObject) => {
      enqueueSnackbar(message, { variant: 'success', ...options })
    },
    error: (message: string, options?: OptionsObject) => {
      enqueueSnackbar(message, { variant: 'error', ...options })
    },
    warning: (message: string, options?: OptionsObject) => {
      enqueueSnackbar(message, { variant: 'warning', ...options })
    },
    info: (message: string, options?: OptionsObject) => {
      enqueueSnackbar(message, { variant: 'info', ...options })
    },
  }

  return toast
}
