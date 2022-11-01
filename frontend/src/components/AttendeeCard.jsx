import React from "react";
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';

export default function AttendeeCard(props) {
  const {name,attendance_duration,attendance_percentage} = props.attendee;
  return (
    <Card variant="outlined" sx={{margin:1, maxWidth: 200, }} >
    <CardContent color="black">
      <Typography sx={{ fontSize: 16 }} color="text.secondary" gutterBottom>
       {name}
      </Typography>
      <Typography variant="h5" component="div">
        {attendance_duration} mins
      </Typography>
      <Typography sx={{ mb: 1.5 }} color="text.secondary">
        {attendance_percentage} %
      </Typography>
    </CardContent>
    </Card>
  );
}