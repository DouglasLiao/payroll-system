import { Box, Typography, Paper, TextField, Button, Stack } from '@mui/material';

export default function TimeAdjustments() {
  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 600, margin: '0 auto' }}>
      <Typography variant="h4" fontWeight={700} mb={3}>
        Solicitar Ajuste de Ponto
      </Typography>

      <Paper sx={{ p: 3, borderRadius: 3 }}>
        <Stack spacing={3}>
          <Typography variant="body1" color="text.secondary">
            Caso tenha esquecido de bater o ponto ou tenha ocorrido um erro, preencha os dados abaixo. 
            A aprovação ficará a critério do Administrador da Empresa.
          </Typography>

          <TextField 
            label="Data da Ocorrência" 
            type="date" 
            fullWidth 
            InputLabelProps={{ shrink: true }}
          />
          <TextField 
            label="Horário (Entrada/Saída)" 
            type="time" 
            fullWidth 
            InputLabelProps={{ shrink: true }}
          />
          <TextField 
            label="Justificativa" 
            multiline 
            rows={4} 
            fullWidth 
            placeholder="Descreva o motivo do ajuste..."
          />

          <Button variant="contained" size="large" sx={{ mt: 2 }}>
            Enviar Solicitação
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
