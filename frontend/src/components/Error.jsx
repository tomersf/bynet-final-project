import React from "react";
import Lottie from "react-lottie"

import "../App.css"
import errorAnimation from '../animations/errorAnimation.json'

export default function Error(props) {
    const defaultOptions = {
        loop: true,
        autoplay: true,
        animationData: errorAnimation,
        rendererSettings: {
        preserveAspectRatio: "xMidYMid slice",
        },
    };
    const {message} = props;
    return (
        <div className="Error">
            <Lottie options={defaultOptions} height={300} width={400} />
            <h4 style={{color:'white'}}>{message}</h4>
        </div>
    )
}