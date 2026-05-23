import { Box, Typography, Paper, Grid, Card, CardContent } from '@mui/material';

// Mocked data to visually demonstrate the calendar summary
const stats = [
  { label: 'Horas Extras', value: '+ 12h 30m', color: 'success.main' },
  { label: 'Horas em Débito', value: '- 3h 15m', color: 'error.main' },
  { label: 'Dias Faltantes', value: '1 Dia', color: 'warning.main' },
  { label: 'Dias Trabalhados', value: '18 Dias', color: 'text.primary' }
];

export default function ScheduleCalendar() {
  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Typography variant="h4" fontWeight={700} mb={3}>
        Calendário e Histórico de Jornada
      </Typography>

      <Grid container spacing={3} mb={4}>
        {stats.map((stat, idx) => (
          <Grid size={{ xs: 12, sm: 6, md: 3 }} key={idx}>
            <Card sx={{ borderRadius: 3 }}>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  {stat.label}
                </Typography>
                <Typography variant="h5" fontWeight={700} color={stat.color}>
                  {stat.value}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Paper sx={{ p: 3, borderRadius: 3, minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          [ Visualização do Calendário de Espelho de Ponto (Em Breve) ]
        </Typography>
      </Paper>
    </Box>
  );
}
