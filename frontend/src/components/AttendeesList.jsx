import React from 'react'
import Grid from '@mui/material/Grid';

import Error from './Error'
import AttendeeCard from './AttendeeCard';

export default function AttendeesList({attendees}) {
  if (attendees.length === 0) {
    return (
      <Error message="Seems that there is no attendees!" />
    )
  }
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
