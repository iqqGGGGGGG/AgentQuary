param(
  [string]$OutputDirectory = (Join-Path $PSScriptRoot '..\src\assets\tab-icons')
)

$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing

$size = 81
$scale = $size / 24.0
$colors = @{
  Default = [System.Drawing.ColorTranslator]::FromHtml('#8B7FA3')
  Active = [System.Drawing.ColorTranslator]::FromHtml('#7C5CFC')
}

function New-IconCanvas {
  $bitmap = [System.Drawing.Bitmap]::new($size, $size, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
  $graphics.Clear([System.Drawing.Color]::Transparent)
  $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
  $graphics.ScaleTransform($scale, $scale)
  return @($bitmap, $graphics)
}

function New-IconPen([System.Drawing.Color]$Color) {
  $pen = [System.Drawing.Pen]::new($Color, 2.0)
  $pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
  $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
  $pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
  return $pen
}

function New-RoundedRectanglePath([single]$X, [single]$Y, [single]$Width, [single]$Height, [single]$Radius) {
  $path = [System.Drawing.Drawing2D.GraphicsPath]::new()
  $diameter = $Radius * 2
  $path.AddArc($X, $Y, $diameter, $diameter, 180, 90)
  $path.AddArc($X + $Width - $diameter, $Y, $diameter, $diameter, 270, 90)
  $path.AddArc($X + $Width - $diameter, $Y + $Height - $diameter, $diameter, $diameter, 0, 90)
  $path.AddArc($X, $Y + $Height - $diameter, $diameter, $diameter, 90, 90)
  $path.CloseFigure()
  return $path
}

function Save-Icon([string]$Name, [System.Drawing.Color]$Color, [scriptblock]$Draw) {
  $canvas = New-IconCanvas
  $bitmap = $canvas[0]
  $graphics = $canvas[1]
  $pen = New-IconPen $Color

  try {
    & $Draw $graphics $pen
    $bitmap.Save((Join-Path $OutputDirectory $Name), [System.Drawing.Imaging.ImageFormat]::Png)
  }
  finally {
    $pen.Dispose()
    $graphics.Dispose()
    $bitmap.Dispose()
  }
}

$drawHome = {
  param($graphics, $pen)

  $door = [System.Drawing.Drawing2D.GraphicsPath]::new()
  $door.StartFigure()
  $door.AddLine(15, 21, 15, 13)
  $door.AddBezier(15, 13, 15, 12.45, 14.55, 12, 14, 12)
  $door.AddLine(14, 12, 10, 12)
  $door.AddBezier(10, 12, 9.45, 12, 9, 12.45, 9, 13)
  $door.AddLine(9, 13, 9, 21)
  $graphics.DrawPath($pen, $door)
  $door.Dispose()

  $house = [System.Drawing.Drawing2D.GraphicsPath]::new()
  $house.StartFigure()
  $house.AddBezier(3, 10, 3, 9.39, 3.28, 8.84, 3.71, 8.47)
  $house.AddLine(3.71, 8.47, 10.71, 2.47)
  $house.AddBezier(10.71, 2.47, 11.08, 2.15, 11.58, 1.84, 12, 1.84)
  $house.AddBezier(12, 1.84, 12.42, 1.84, 12.92, 2.15, 13.29, 2.47)
  $house.AddLine(13.29, 2.47, 20.29, 8.47)
  $house.AddBezier(20.29, 8.47, 20.72, 8.84, 21, 9.39, 21, 10)
  $house.AddLine(21, 10, 21, 19)
  $house.AddBezier(21, 19, 21, 20.1, 20.1, 21, 19, 21)
  $house.AddLine(19, 21, 5, 21)
  $house.AddBezier(5, 21, 3.9, 21, 3, 20.1, 3, 19)
  $house.CloseFigure()
  $graphics.DrawPath($pen, $house)
  $house.Dispose()
}

$drawHistory = {
  param($graphics, $pen)

  foreach ($y in @(6, 10, 14, 18)) {
    $graphics.DrawLine($pen, 2, $y, 6, $y)
  }
  $notebook = New-RoundedRectanglePath 4 2 16 20 2
  $graphics.DrawPath($pen, $notebook)
  $notebook.Dispose()
  $graphics.DrawLine($pen, 15, 2, 15, 22)
  foreach ($y in @(7, 12, 17)) {
    $graphics.DrawLine($pen, 15, $y, 20, $y)
  }
}

$drawProfile = {
  param($graphics, $pen)

  $graphics.DrawEllipse($pen, 7, 3, 10, 10)
  $shoulders = [System.Drawing.Drawing2D.GraphicsPath]::new()
  $shoulders.StartFigure()
  $shoulders.AddBezier(20, 21, 20, 16.58, 16.42, 13, 12, 13)
  $shoulders.AddBezier(12, 13, 7.58, 13, 4, 16.58, 4, 21)
  $graphics.DrawPath($pen, $shoulders)
  $shoulders.Dispose()
}

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null

Save-Icon 'home.png' $colors.Default $drawHome
Save-Icon 'home-active.png' $colors.Active $drawHome
Save-Icon 'history.png' $colors.Default $drawHistory
Save-Icon 'history-active.png' $colors.Active $drawHistory
Save-Icon 'profile.png' $colors.Default $drawProfile
Save-Icon 'profile-active.png' $colors.Active $drawProfile

Write-Output "Rendered six TabBar icons to $OutputDirectory"
