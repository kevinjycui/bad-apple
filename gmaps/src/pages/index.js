import React from "react"
import Helmet from "react-helmet"
import axios from 'axios'

import { withScriptjs, withGoogleMap, GoogleMap, Marker } from "react-google-maps"
// require('dotenv').config()

// styles
const pageStyles = {
  color: "#232129",
  padding: "0",
  fontFamily: "-apple-system, Roboto, sans-serif, serif",
}

const MyMapComponent = withScriptjs(withGoogleMap((props) =>
  <GoogleMap
    defaultZoom={4}
    defaultCenter={{ lat: 30, lng: 70 }}
  >
    {props.markerProps}
  </GoogleMap>
))

const request = async (url) => {
  try {
    const response = await axios.get(url);
    return response.data;
  } catch (err) {
    console.log(err);
    return {};
  }
};

var frame_data = null;
const width = 36;
const height = 28;

const gmaps_api_key = "ENTER GOOGLE MAPS API KEY HERE"


class Index extends React.Component {

  constructor(props) {
    super(props);
    this.state = { 
      index: 0,
      seconds: parseInt(props.startTimeInSeconds, 10) || 0,
      markers: [],
    };
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  tick() {

    var i = 0;

    var marker_props = [];

    if (frame_data !== null && this.state.index < 4382) {
      for (var x=0; x<height; x++) {
        for (var y=0; y<width; y++) {
          if (frame_data[this.state.index][x][y] === 1) {
            marker_props.push(<Marker key={i} position={{ lat: - x * 60/height + 55, lng: y * 100/width + 20 + 3.6 }} />);
            marker_props.push(<Marker key={i+1} position={{ lat: - x * 60/height + 55, lng: y * 100/width + 20 }} />);
            marker_props.push(<Marker key={i+2} position={{ lat: - x * 60/height + 55, lng: y * 100/width + 20 - 3.6 }} />);
            i+=3;
          }
        }
      }

      this.setState(state => ({
        seconds: state.seconds + 1/24,
        index: state.index + 1,
        markers: marker_props,
      }));

    }

  }

  componentDidMount() {
    this.interval = setInterval(() => this.tick(), 4 * 1000/24);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }

  formatTime(secs) {
    let hours   = Math.floor(secs / 3600);
    let minutes = Math.floor(secs / 60) % 60;
    let seconds = Math.floor(secs % 60);
    return [hours, minutes, seconds]
        .map(v => ('' + v).padStart(2, '0'))
        .filter((v,i) => v !== '00' || i > 0)
        .join(':');
  }

  GetData = async() => {
    frame_data = await request('http://localhost:8000/frame_data.json');
    console.log(frame_data[0])
  }

  handleSubmit(event) {
    console.log('Clicked')
    this.GetData();
  }

  render() {

    return (
      <main style={pageStyles}>
      <div style={{
        padding: 0
      }}>
        <Helmet>
          <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous" />
          <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/js/bootstrap.bundle.min.js" integrity="sha384-ygbV9kiqUc6oa4msXn9868pTtWMgiQaeYH7/t7LECLbyPA2x65Kgf80OJFdroafW" crossorigin="anonymous" defer></script>
        </Helmet>

        <button onClick={this.handleSubmit}>&ensp;开始</button>
    
        {this.formatTime(this.state.seconds)}
        
        <MyMapComponent
          googleMapURL={`https://maps.googleapis.com/maps/api/js?key=${gmaps_api_key}&v=3.exp&language=zh&libraries=geometry,drawing,places`}
          loadingElement={<div style={{ height: `100%` }} />}
          containerElement={<div style={{ height: `1000px` }} />}
          mapElement={<div style={{ height: `100%` }} />}
          markerProps={this.state.markers}
        >

        </MyMapComponent>
      </div>
    </main>
    )
  }
}

export default Index
