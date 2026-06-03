import Image from 'next/image'
import React from 'react'

const ImageContainer = ({src, alt, w=700, h=600}) => {
  return (
    <div className="d-flex justify-content-center w-100">
      <Image src={src} alt={alt} width={w || 700} height={h || 600} />
    </div>
  )
}

export default ImageContainer