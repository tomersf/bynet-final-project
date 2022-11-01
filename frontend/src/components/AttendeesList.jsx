import React from 'react'
import Grid from '@mui/material/Grid';

import AttendeeCard from './AttendeeCard';

export default function AttendeesList({attendees}) {
  return (
        <Grid container spacing={4} >
          {attendees.map((attendee) => (
            <Grid item xs={6} md={4} lg={2} key={attendee.id}>
              <AttendeeCard
              attendee={attendee}
              />
              </Grid>
          ))}
        </Grid>
  );
}
