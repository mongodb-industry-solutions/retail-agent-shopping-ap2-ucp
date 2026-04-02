import Image from 'next/image'
import React from 'react'

const ImageContainer = ({src, alt, w=500, h=400}) => {
  return (
    <div className="d-flex justify-content-center w-100">
      <Image src={src} alt={alt} width={w || 500} height={h || 400} />
    </div>
  )
}

export default ImageContainer