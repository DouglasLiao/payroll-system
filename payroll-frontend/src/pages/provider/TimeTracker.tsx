import { useState, useEffect } from 'react';
import { Box, Typography, Button, Paper, Stack, Alert } from '@mui/material';
import { LocationMap } from '@payroll/design-system';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';

export default function TimeTracker() {
  const [loadingLoc, setLoadingLoc] = useState(false);
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [errorStr, setErrorStr] = useState<string | null>(null);
  const [clockedIn, setClockedIn] = useState(false);

  // Fetch location on mount or before clock in
  const fetchLocation = () => {
    setLoadingLoc(true);
    setErrorStr(null);
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
          setLoadingLoc(false);
        },
        () => {
          setErrorStr('Falha ao obter localização. Permita o acesso ao GPS do seu navegador.');
          setLoadingLoc(false);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      );
    } else {
      setErrorStr('Geolocalização não é suportada neste navegador.');
      setLoadingLoc(false);
    }
  };

  useEffect(() => {
    fetchLocation();
  }, []);

  const handleToggleClock = () => {
    if (!location && !clockedIn) {
      setErrorStr('É necessário permitir a localização para bater o ponto.');
      return;
    }
    // TODO: Send to backend api/time-records
    setClockedIn(!clockedIn);
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 800, margin: '0 auto' }}>
      <Typography variant="h4" fontWeight={700} mb={3}>
        Bater Ponto
      </Typography>

      <Paper sx={{ p: 3, borderRadius: 3, mb: 4 }}>
        <Stack spacing={3}>
          <Box>
            <Typography variant="h6" mb={1}>
              Sua Localização Atual
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              Para registrar o ponto, sua localização precisa deve ser enviada.
            </Typography>

            {errorStr && (
              <Alert severity="error" sx={{ mb: 2 }}>{errorStr}</Alert>
            )}

            <Box sx={{ height: { xs: 250, md: 350 }, width: '100%', mb: 2 }}>
              <LocationMap 
                latitude={location?.lat ?? null} 
                longitude={location?.lng ?? null} 
                height="100%" 
                width="100%" 
              />
            </Box>

            <Button 
              variant="text" 
              onClick={fetchLocation} 
              disabled={loadingLoc}
            >
              {loadingLoc ? 'Obtendo localização...' : 'Atualizar Localização'}
            </Button>
          </Box>

          <Button
            variant="contained"
            color={clockedIn ? 'error' : 'primary'}
            size="large"
            startIcon={clockedIn ? <StopIcon /> : <PlayArrowIcon />}
            onClick={handleToggleClock}
            disabled={loadingLoc || (!location && !clockedIn)}
            sx={{ py: 2, fontSize: '1.2rem', borderRadius: 4 }}
          >
            {clockedIn ? 'Finalizar Jornada (Saída)' : 'Registrar Ponto (Entrada)'}
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
