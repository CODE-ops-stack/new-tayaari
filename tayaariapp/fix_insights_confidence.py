import codecs
with codecs.open('app/src/main/java/com/example/ui/screens/InsightsDashboardScreen.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if 'var blindSpots by remember' in line:
        new_lines.append(line)
        new_lines.append('    var confidenceReport by remember { mutableStateOf<LocalRepository.ConfidenceCalibrationReport?>(null) }\n')
        continue
    
    if 'blindSpots = localRepository.getBlindSpots()' in line:
        new_lines.append(line)
        new_lines.append('            confidenceReport = localRepository.getConfidenceCalibrationReport()\n')
        continue
    
    if 'else if (blindSpots.isEmpty()) {' in line:
        new_lines.append('        } else if (blindSpots.isEmpty() && confidenceReport == null) {\n')
        continue
        
    if 'text = "Your Blind Spots",' in line:
        insert = '''
                if (confidenceReport != null) {
                    item {
                        Text(
                            text = "Confidence Calibration",
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                    
                    if (confidenceReport!!.overconfidenceDetected) {
                        item {
                            Card(
                                modifier = Modifier.fillMaxWidth(),
                                colors = CardDefaults.cardColors(containerColor = Color.White),
                                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                            ) {
                                Row(
                                    modifier = Modifier.padding(16.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(Icons.Default.Warning, contentDescription = "Warning", tint = Color.Red)
                                    Spacer(modifier = Modifier.width(16.dp))
                                    Column {
                                        Text("Overconfidence", style = MaterialTheme.typography.titleSmall)
                                        Text(confidenceReport!!.overconfidenceMessage, style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                                    }
                                }
                            }
                        }
                    }
                    
                    if (confidenceReport!!.underconfidenceDetected) {
                        item {
                            Card(
                                modifier = Modifier.fillMaxWidth(),
                                colors = CardDefaults.cardColors(containerColor = Color.White),
                                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                            ) {
                                Row(
                                    modifier = Modifier.padding(16.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(Icons.Default.Warning, contentDescription = "Warning", tint = Color(0xFFE65100))
                                    Spacer(modifier = Modifier.width(16.dp))
                                    Column {
                                        Text("Underconfidence", style = MaterialTheme.typography.titleSmall)
                                        Text(confidenceReport!!.underconfidenceMessage, style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                                    }
                                }
                            }
                        }
                    }
                }
                
                if (blindSpots.isNotEmpty()) {
'''
        new_lines.append(insert)
        new_lines.append(line)
        continue
        
    if 'items(blindSpots) { stat ->' in line:
        new_lines.append('                }\n')
        new_lines.append(line)
        continue

    new_lines.append(line)

with codecs.open('app/src/main/java/com/example/ui/screens/InsightsDashboardScreen.kt', 'w', 'utf-8') as f:
    f.writelines(new_lines)
