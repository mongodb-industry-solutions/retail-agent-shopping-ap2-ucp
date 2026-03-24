import Image from 'next/image'
import React from 'react'

const ImageContainer = ({src, alt, w=null, h=null}) => {
  return (
    <div className="d-flex justify-content-center w-100">
      <Image src={src} alt={alt} width={w || 400} height={h || 300} />
    </div>
  )
}

export default ImageContainer