# KinderSort Lite Project Report

## Introduction

KinderSort Lite is an AI-based student photo sorting system designed for kindergartens.

## System Overview

KinderSort Lite is an offline AI-based image sorting system designed for kindergarten teachers. The system allows users to upload reference photos and event photos before automatically matching student faces and sorting images into the correct folders.

The system consists of three main components:

1. Face Detection
2. Face Recognition
3. Automatic Folder Classification

Users only need to select the reference folder, event folder, and output folder before starting the sorting process. The system then performs offline image processing and generates organized student folders automatically.

## Ethical Issues

### Privacy Concerns

KinderSort Lite processes children's photographs, which are considered sensitive personal data. Unauthorized access to these images may create privacy risks for students and schools.

### AI Bias

The system may incorrectly classify images due to lighting conditions, image quality, face angles, or incomplete reference photos. This could result in photos being assigned to the wrong student folder.

### Accessibility

Many kindergartens operate using low-specification computers. Therefore, AI solutions should remain lightweight, affordable, and accessible to low-resource users.

### Incorrect Classification Risks

Incorrect face recognition may lead to privacy concerns and reduce trust in the system. Teachers may need to manually verify results before distributing photos.

## Professional Ethics and ACM Code

The development of KinderSort Lite follows several principles from the ACM Code of Ethics.

### Avoid Harm

Developers should reduce the risk of incorrect image classification because mistakes may affect students, teachers, and parents.

### Respect Privacy

Children's photos contain personal information and should be protected from unauthorized access.

### Be Honest and Transparent

Users should understand the limitations of the system. The software may not achieve 100% accuracy in every situation.

### Act in the Public Interest

The system should improve teacher productivity while ensuring privacy, security, and fairness for all users.

## Recommendations

Several improvements can be implemented in future versions of KinderSort Lite.

1. Add stronger encryption to protect student photos.
2. Implement user authentication and access control.
3. Conduct regular bias testing to improve fairness.
4. Improve accuracy using larger datasets.
5. Add automatic error reporting for incorrect classifications.

## Reflection

This project helped us understand that AI development is not only about improving accuracy. Privacy, fairness, accessibility, and professional responsibility are equally important.

We also learned that low-resource optimization is necessary because many schools use older computers with limited hardware capabilities. By using CPU-only processing and lightweight AI methods, the system remains practical and accessible.

Overall, this project improved our understanding of both artificial intelligence and computing ethics.

## Stakeholder Analysis

The main stakeholders of KinderSort Lite include teachers, students, parents, and school management.

Teachers benefit from reduced manual sorting work and improved productivity. Students and parents benefit from faster access to organized event photos. However, incorrect image classification may create privacy concerns if photos are placed in the wrong folder.

Therefore, all stakeholders should be considered when designing and deploying AI systems in educational environments.

## Low Resource Environment Considerations

KinderSort Lite is designed for schools with limited hardware resources. By using CPU-only processing and lightweight face recognition techniques, the system can operate without requiring expensive GPUs.

This helps improve accessibility and allows more educational institutions to benefit from AI technology regardless of budget limitations.